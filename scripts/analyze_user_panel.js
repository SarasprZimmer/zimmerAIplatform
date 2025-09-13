const fs = require("fs");
const path = require("path");
const { globby } = require("globby");

// Load the config
const { DESIRED_FEATURES } = require("./feature_inventory.config.js");

const PANEL_ROOT = path.join(process.cwd(), "zimmer_user_panel");
const SRC_DIRS = ["pages", "components", "app"].map(d => path.join(PANEL_ROOT, d));

// Simple extractors
const RX_API = /apiFetch\(\s*`?["'`](?<path>\/api\/[^"'`?]+(?:\?[^"'`]*)?)["'`]/g;
const RX_FETCH = /fetch\(\s*`?["'`](?<path>\/api\/[^"'`?]+(?:\?[^"'`]*)?)["'`]/g;
const RX_METHOD = /method\s*:\s*["'`](GET|POST|PUT|PATCH|DELETE)/ig;
const RX_HREF = /href\s*=\s*["'`](?<href>\/[^"'`]+)["'`]/g;
const RX_TITLE = /<h1[^>]*>(?<title>[^<]+)<\/h1>|<title>(?<title2>[^<]+)<\/title>/i;
const RX_RECHARTS = /\b(BarChart|LineChart|PieChart|AreaChart)\b/;
const RX_ACTION_HINTS = /\b(onClick|onSubmit|POST|PUT|PATCH|DELETE|form|button)\b/;

function guessRouteFromFile(f) {
  // pages/foo/bar.tsx -> /foo/bar
  const rel = path.relative(path.join(PANEL_ROOT, "pages"), f).replace(/\\/g, "/");
  if (!rel || rel.startsWith("..")) return "";
  let route = "/" + rel.replace(/index\.tsx?$/, "").replace(/\.tsx?$/, "");
  route = route.replace(/\/+/g, "/");
  if (route.endsWith("/")) route = route.slice(0, -1);
  return route || "/";
}

async function main() {
  console.log("🔍 Starting User Panel Feature Analysis...");
  console.log(`📁 Panel root: ${PANEL_ROOT}`);
  
  // gather files
  console.log("🔍 Searching in directories:", SRC_DIRS);
  const files = await globby(SRC_DIRS.map(d => `${d}/**/*.{ts,tsx}`), { 
    gitignore: true, 
    ignore: ["**/node_modules/**"] 
  });

  console.log(`📄 Found ${files.length} files to analyze`);
  let filesToProcess = files;
  
  if (files.length === 0) {
    console.log("🔍 Trying alternative search...");
    const altFiles = await globby(["zimmer_user_panel/**/*.{ts,tsx}"], { 
      gitignore: true, 
      ignore: ["**/node_modules/**"] 
    });
    console.log(`📄 Alternative search found ${altFiles.length} files`);
    if (altFiles.length > 0) {
      console.log("📄 Sample files:", altFiles.slice(0, 5));
      filesToProcess = altFiles;
    }
  }

  const pages = [];
  for (const f of filesToProcess) {
    const code = fs.readFileSync(f, "utf8");
    const isPage = f.includes("/pages/");
    if (!isPage) continue;

    const endpoints = [];
    const hrefs = [];
    let m;

    // apiFetch endpoints
    while ((m = RX_API.exec(code))) {
      endpoints.push({ path: (m.groups?.path || "").trim() });
    }
    // raw fetch endpoints
    while ((m = RX_FETCH.exec(code))) {
      endpoints.push({ path: (m.groups?.path || "").trim() });
    }
    // naive method detection
    const methods = Array.from(code.matchAll(RX_METHOD)).map(x => x[1]?.toUpperCase());
    // attach method to first N endpoints (best-effort)
    endpoints.forEach((e, i) => { if (!e.method && methods[i]) e.method = methods[i]; });

    // hrefs
    while ((m = RX_HREF.exec(code))) {
      hrefs.push((m.groups?.href || "").trim());
    }

    // title & charts & action hints
    const t = RX_TITLE.exec(code);
    const title = t?.groups?.title || t?.groups?.title2;
    const charts = RX_RECHARTS.test(code) ? Array.from(code.matchAll(/\b(BarChart|LineChart|PieChart|AreaChart)\b/g)).map(x => x[1]) : [];
    const actionsHint = RX_ACTION_HINTS.test(code);

    // naive component names (import lines)
    const components = Array.from(code.matchAll(/import\s+([\s\S]*?)\s+from\s+["'][^"']+["']/g))
      .map(g => g[1])
      .flatMap(s => s.split(/[{},\s]+/).map(x => x.trim()).filter(Boolean))
      .filter(n => /^[A-Z][A-Za-z0-9_]*$/.test(n))
      .slice(0, 20);

    const route = guessRouteFromFile(f);
    pages.push({ 
      file: path.relative(PANEL_ROOT, f), 
      route, 
      title, 
      endpoints, 
      hrefs: Array.from(new Set(hrefs)), 
      components, 
      charts, 
      actionsHint 
    });
  }

  console.log(`📊 Analyzed ${pages.length} pages`);

  // build feature map per route
  const featureByRoute = {};
  for (const p of pages) {
    featureByRoute[p.route] = featureByRoute[p.route] || { endpoints: [], methods: [], charts: [], hrefs: [], components: [] };
    featureByRoute[p.route].endpoints.push(...p.endpoints.map(e => e.path));
    featureByRoute[p.route].methods.push(...p.endpoints.map(e => e.method || "GET?"));
    featureByRoute[p.route].charts.push(...p.charts);
    featureByRoute[p.route].hrefs.push(...p.hrefs);
    featureByRoute[p.route].components.push(...p.components);
  }
  // dedupe
  Object.values(featureByRoute).forEach(v => {
    v.endpoints = Array.from(new Set(v.endpoints));
    v.methods = Array.from(new Set(v.methods));
    v.charts = Array.from(new Set(v.charts));
    v.hrefs = Array.from(new Set(v.hrefs));
    v.components = Array.from(new Set(v.components)).slice(0, 30);
  });

  // (optional) load OpenAPI to check coverage
  let openapi = null;
  if (process.env.OPENAPI) {
    console.log("🔗 Attempting to fetch OpenAPI spec...");
    try {
      const envLocal = path.join(PANEL_ROOT, ".env.local");
      let base = process.env.NEXT_PUBLIC_API_BASE_URL || "";
      if (!base && fs.existsSync(envLocal)) {
        const env = fs.readFileSync(envLocal, "utf8");
        const m = env.match(/NEXT_PUBLIC_API_BASE_URL\s*=\s*(.+)/);
        base = m?.[1]?.trim() || "";
      }
      if (base) {
        const res = await fetch(base.replace(/\/+$/, "") + "/openapi.json");
        if (res.ok) {
          openapi = await res.json();
          console.log("✅ OpenAPI spec loaded successfully");
        } else {
          console.log("⚠️ OpenAPI spec not available");
        }
      } else {
        console.log("⚠️ No API base URL found");
      }
    } catch (e) {
      console.log("⚠️ Failed to load OpenAPI spec:", e);
    }
  }

  // match desired features to discovered endpoints
  const featureCoverage = DESIRED_FEATURES.map(df => {
    const usedByRoutes = [];
    const matchedEndpoints = [];
    if (df.expectedEndpoints) {
      for (const route of Object.keys(featureByRoute)) {
        for (const ep of featureByRoute[route].endpoints) {
          if (df.expectedEndpoints.some(pat => matchEndpointPattern(ep, pat))) {
            usedByRoutes.push(route);
            matchedEndpoints.push(ep);
          }
        }
      }
    }
    return { 
      key: df.key, 
      title: df.title, 
      usedByRoutes: Array.from(new Set(usedByRoutes)), 
      matchedEndpoints: Array.from(new Set(matchedEndpoints)) 
    };
  });

  // compute "not covered" desired features
  const missing = featureCoverage.filter(fc => fc.usedByRoutes.length === 0);

  // write JSON + Markdown
  const outJson = {
    generatedAt: new Date().toISOString(),
    pages,
    byRoute: featureByRoute,
    desired: DESIRED_FEATURES,
    coverage: featureCoverage,
    missingDesiredFeatures: missing,
    openapiLoaded: Boolean(openapi),
  };
  fs.writeFileSync(path.join(process.cwd(), "feature_inventory.json"), JSON.stringify(outJson, null, 2), "utf8");

  const md = renderMarkdownReport(pages, featureByRoute, featureCoverage, missing);
  fs.writeFileSync(path.join(process.cwd(), "REPORT_feature_inventory.md"), md, "utf8");

  console.log("✅ Analysis complete!");
  console.log(`📄 Generated: REPORT_feature_inventory.md`);
  console.log(`📄 Generated: feature_inventory.json`);
  console.log(`📊 Found ${pages.length} pages, ${Object.keys(featureByRoute).length} routes`);
  console.log(`🎯 Coverage: ${featureCoverage.filter(f => f.usedByRoutes.length > 0).length}/${featureCoverage.length} desired features`);
  console.log(`❌ Missing: ${missing.length} desired features not found`);
}

function matchEndpointPattern(ep, pat) {
  // Convert patterns like /api/automations/* to regex
  const esc = pat.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\\\*/g, ".*");
  const rx = new RegExp("^" + esc + "$");
  return rx.test(ep);
}

function renderMarkdownReport(pages, byRoute, coverage, missing) {
  const lines = [];
  lines.push("# Zimmer User Panel — Feature Inventory");
  lines.push("");
  lines.push(`**Generated**: ${new Date().toLocaleString()}`);
  lines.push(`**Pages Analyzed**: ${pages.length}`);
  lines.push(`**Routes Found**: ${Object.keys(byRoute).length}`);
  lines.push(`**Desired Features**: ${coverage.length}`);
  lines.push(`**Covered Features**: ${coverage.filter(f => f.usedByRoutes.length > 0).length}`);
  lines.push(`**Missing Features**: ${missing.length}`);
  lines.push("");

  lines.push("## 📄 Pages Scanned");
  lines.push("");
  for (const p of pages.sort((a,b)=>a.route.localeCompare(b.route))) {
    lines.push(`### ${p.route}`);
    if (p.title) lines.push(`- **Title**: ${p.title}`);
    if (p.endpoints.length) lines.push(`- **Endpoints**: ${p.endpoints.map((e)=>`\`${e.path||e}\``).join(", ")}`);
    if (p.charts.length) lines.push(`- **Charts**: ${p.charts.join(", ")}`);
    if (p.actionsHint) lines.push(`- **Actions**: form/buttons detected`);
    if (p.hrefs.length) lines.push(`- **Links**: ${p.hrefs.join(", ")}`);
    if (p.components.length) lines.push(`- **Components**: ${p.components.slice(0, 10).join(", ")}${p.components.length > 10 ? "..." : ""}`);
    lines.push("");
  }

  lines.push("## 🗺️ Feature Map by Route");
  lines.push("");
  for (const route of Object.keys(byRoute).sort()) {
    const v = byRoute[route];
    lines.push(`### ${route}`);
    lines.push(`- **Endpoints**: ${v.endpoints.map(e=>`\`${e}\``).join(", ") || "—"}`);
    lines.push(`- **Methods**: ${v.methods.join(", ") || "—"}`);
    lines.push(`- **Charts**: ${v.charts.join(", ") || "—"}`);
    lines.push(`- **Components**: ${v.components.slice(0, 10).join(", ") || "—"}${v.components.length > 10 ? "..." : ""}`);
    lines.push("");
  }

  lines.push("## 🎯 Desired Feature Coverage");
  lines.push("");
  for (const c of coverage) {
    const status = c.usedByRoutes.length ? "✅" : "❌";
    lines.push(`- ${status} **${c.title}** (\`${c.key}\`)`);
    if (c.usedByRoutes.length) {
      lines.push(`  - **Routes**: ${c.usedByRoutes.join(", ")}`);
      lines.push(`  - **Endpoints**: ${c.matchedEndpoints.map((e)=>`\`${e}\``).join(", ")}`);
    }
    lines.push("");
  }

  if (missing.length) {
    lines.push("## ❌ Missing Desired Features");
    lines.push("");
    lines.push("These features are defined in the desired feature list but not found on any page:");
    lines.push("");
    for (const m of missing) {
      lines.push(`- ❌ **${m.title}** (\`${m.key}\`)`);
      if (m.expectedEndpoints) {
        lines.push(`  - Expected endpoints: ${m.expectedEndpoints.map((e) => `\`${e}\``).join(", ")}`);
      }
    }
    lines.push("");
  }

  // overlap quickview
  lines.push("## 🔄 Endpoint Overlap Analysis");
  lines.push("");
  const epToRoutes = {};
  for (const r of Object.keys(byRoute)) {
    for (const ep of byRoute[r].endpoints) {
      epToRoutes[ep] = epToRoutes[ep] || new Set();
      epToRoutes[ep].add(r);
    }
  }
  const overlaps = Object.entries(epToRoutes).filter(([_, routes]) => routes.size > 1);
  if (overlaps.length === 0) {
    lines.push("- *(No endpoint overlaps found)*");
  } else {
    lines.push("Endpoints used on multiple routes:");
    for (const [ep, routes] of overlaps) {
      lines.push(`- \`${ep}\` → ${Array.from(routes).sort().join(", ")}`);
    }
  }
  lines.push("");

  // Summary statistics
  lines.push("## 📊 Summary Statistics");
  lines.push("");
  const totalEndpoints = new Set(Object.values(byRoute).flatMap(v => v.endpoints)).size;
  const totalComponents = new Set(Object.values(byRoute).flatMap(v => v.components)).size;
  const totalCharts = new Set(Object.values(byRoute).flatMap(v => v.charts)).size;
  
  lines.push(`- **Total Unique Endpoints**: ${totalEndpoints}`);
  lines.push(`- **Total Unique Components**: ${totalComponents}`);
  lines.push(`- **Total Chart Types**: ${totalCharts}`);
  lines.push(`- **Feature Coverage Rate**: ${Math.round((coverage.filter(f => f.usedByRoutes.length > 0).length / coverage.length) * 100)}%`);
  lines.push("");

  return lines.join("\n");
}

main().catch(e => { 
  console.error("❌ Analysis failed:", e); 
  process.exit(1); 
});
