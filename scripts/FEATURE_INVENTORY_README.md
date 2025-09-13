# Feature Inventory — How to run

From the monorepo root:

## Quick run (no OpenAPI)
```bash
npm run analyze:features
```
This scans **zimmer_user_panel/pages/** and writes:
- **REPORT_feature_inventory.md**
- **feature_inventory.json**

## Strict mode (compare with OpenAPI)
Export your API base (or set in zimmer_user_panel/.env.local as NEXT_PUBLIC_API_BASE_URL), then:
```bash
NEXT_PUBLIC_API_BASE_URL=${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"} OPENAPI=1 npm run analyze:features:strict
```
If available, it will fetch `$API/openapi.json` and mark desired features as covered/missing based on endpoint presence on pages.

## Customize the desired feature list
Edit `scripts/feature_inventory.config.ts` to reflect your real feature set and expected endpoints.

## What you get
- **Pages Scanned**: each route → endpoints used, links, charts, components
- **Feature Map by Route**: deduped picture of what each page actually does
- **Desired Coverage**: which of your target features appear on any page
- **Missing Desired Features**: any target features not found
- **Overlap**: endpoints reused across multiple pages

This helps decide which pages are redundant and which still need to be implemented.

## Example Output

### Pages Scanned
```
### /dashboard
- Title: داشبورد
- Endpoints: `/api/user/payments`, `/api/user/automations`
- Charts: BarChart, LineChart
- Actions: form/buttons detected
- Components: DashboardLayout, RecentPayments, MyAutomations
```

### Feature Coverage
```
✅ تاریخچه پرداخت (payments.history)
  - Routes: /dashboard, /payment
  - Endpoints: `/api/user/payments`

❌ اعلان‌ها (notifications)
  - Expected endpoints: `/api/notifications`, `/api/notifications/mark-*`
```

### Missing Features
```
❌ اعلان‌ها (notifications)
  - Expected endpoints: `/api/notifications`, `/api/notifications/mark-*`

❌ مصرف هفتگی (usage.weekly)
  - Expected endpoints: `/api/user/usage?range=7d`
```

## Understanding the Results

### Coverage Analysis
- **✅ Covered**: Feature is implemented and endpoints are used
- **❌ Missing**: Feature is defined but no matching endpoints found

### Overlap Analysis
Shows which endpoints are used across multiple pages, helping identify:
- Redundant API calls
- Shared functionality
- Potential optimization opportunities

### Component Analysis
Lists all imported components per page, helping identify:
- Reusable components
- Page-specific components
- Missing component implementations

## Troubleshooting

### No pages found
- Check that `zimmer_user_panel/pages/` directory exists
- Verify file extensions are `.tsx` or `.ts`

### OpenAPI fetch fails
- Ensure backend is running on the specified URL
- Check `NEXT_PUBLIC_API_BASE_URL` environment variable
- Verify `/openapi.json` endpoint is accessible

### Missing dependencies
```bash
npm install globby ts-node
```

## Advanced Usage

### Custom file patterns
Edit the `SRC_DIRS` array in `analyze_user_panel.ts` to include additional directories:
```typescript
const SRC_DIRS = ["pages", "components", "app", "lib"].map(d => path.join(PANEL_ROOT, d));
```

### Custom regex patterns
Modify the regex patterns to detect additional patterns:
```typescript
const RX_CUSTOM_API = /customApiCall\(\s*["']([^"']+)["']/g;
```

### Additional analysis
Extend the `PageInfo` type and analysis logic to include:
- Form validation patterns
- State management usage
- Error handling patterns
- Performance metrics
