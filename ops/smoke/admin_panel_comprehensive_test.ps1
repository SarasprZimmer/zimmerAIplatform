Write-Host "== Zimmer Admin Panel Comprehensive Test =="
Write-Host "=========================================="

# Check if we're in the right directory
if (-not (Test-Path "zimmermanagement/zimmer-admin-dashboard")) {
    Write-Host "❌ Admin dashboard not found. Please run from project root."
    exit 1
}

Push-Location zimmermanagement/zimmer-admin-dashboard

# 0) Environment Check
Write-Host "`nStep 0: Environment & Configuration Check"
Write-Host "----------------------------------------------"
try {
    $envContent = Get-Content .env.local
    Write-Host "✅ .env.local found with $($envContent.Count) lines"
    Write-Host "   API URL: $($envContent | Where-Object { $_ -match 'NEXT_PUBLIC_API_URL' })"
    Write-Host "   Port: $($envContent | Where-Object { $_ -match 'PORT' })"
} catch {
    Write-Host "❌ Environment file issue: $($_.Exception.Message)"
}

# 1) Build & Compilation Test
Write-Host "`nStep 1: Build & Compilation Test"
Write-Host "-------------------------------------"
try {
    Write-Host "Testing build process..."
    npm run build
    Write-Host "✅ Build successful"
} catch {
    Write-Host "❌ Build failed: $($_.Exception.Message)"
}

try {
    Write-Host "Testing TypeScript compilation..."
    npx tsc --noEmit
    Write-Host "✅ TypeScript compilation successful"
} catch {
    Write-Host "❌ TypeScript errors: $($_.Exception.Message)"
}

# 2) Code Quality & Deprecation Check
Write-Host "`nStep 2: Code Quality & Deprecation Check"
Write-Host "----------------------------------------------"
Write-Host "Scanning for deprecated functions..."

$deprecatedFunctions = @(
    "authenticatedFetch",
    "getToken",
    "setToken", 
    "removeToken",
    "getUser",
    "setUser",
    "removeUser"
)

foreach ($func in $deprecatedFunctions) {
    $files = Get-ChildItem -Recurse -Include "*.tsx", "*.ts" | Select-String $func
    if ($files) {
        Write-Host "⚠️  $func usage found in:"
        foreach ($file in $files | Select-Object -First 3) {
            Write-Host "     $($file.Filename):$($file.LineNumber)"
        }
    }
}

# 3) API Endpoint Analysis
Write-Host "`nStep 3: API Endpoint Analysis"
Write-Host "---------------------------------"
Write-Host "Analyzing API calls in components..."

$apiEndpoints = @()
Get-ChildItem -Recurse -Include "*.tsx", "*.ts" | Select-String "api\.(get|post|put|delete)\(['\""]([^'\""]+)['\""]" | ForEach-Object {
    $endpoint = $_.Matches[0].Groups[2].Value
    if ($endpoint -notin $apiEndpoints) {
        $apiEndpoints += $endpoint
    }
}

Write-Host "Found $($apiEndpoints.Count) unique API endpoints:"
foreach ($endpoint in $apiEndpoints | Sort-Object) {
    Write-Host "   $endpoint"
}

# 4) Component Health Check
Write-Host "`nStep 4: Component Health Check"
Write-Host "-----------------------------------"
$components = @(
    "Layout",
    "Sidebar", 
    "ProtectedRoute",
    "Toast",
    "AppErrorBoundary"
)

foreach ($comp in $components) {
    $file = "components/$comp.tsx"
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "✅ $comp.tsx ($size bytes)"
    } else {
        Write-Host "❌ $comp.tsx - MISSING"
    }
}

# 5) Page Health Check
Write-Host "`nStep 5: Page Health Check"
Write-Host "------------------------------"
$pages = @(
    "index",
    "login", 
    "users",
    "automations",
    "payments",
    "tickets",
    "kb-templates",
    "knowledge",
    "backups",
    "kb-monitoring"
)

foreach ($page in $pages) {
    $file = "pages/$page.tsx"
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        $hasErrors = Get-Content $file | Select-String "TODO|FIXME|HACK|console\.log"
        if ($hasErrors) {
            Write-Host "⚠️  $page.tsx ($size bytes) - Has issues"
        } else {
            Write-Host "✅ $page.tsx ($size bytes)"
        }
    } else {
        Write-Host "❌ $page.tsx - MISSING"
    }
}

# 6) Authentication System Check
Write-Host "`nStep 6: Authentication System Check"
Write-Host "----------------------------------------"
$authFiles = @(
    "contexts/AuthContext.tsx",
    "lib/auth.ts",
    "lib/auth-client.ts",
    "lib/api.ts"
)

foreach ($file in $authFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "✅ $file ($size bytes)"
        
        # Check for deprecated usage
        $deprecatedUsage = Get-Content $file | Select-String "authenticatedFetch|getToken|setToken"
        if ($deprecatedUsage) {
            Write-Host "   ⚠️  Contains deprecated functions"
        }
    } else {
        Write-Host "❌ $file - MISSING"
    }
}

# 7) Dependencies & Package Check
Write-Host "`nStep 7: Dependencies & Package Check"
Write-Host "------------------------------------------"
try {
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    Write-Host "Package: $($packageJson.name) v$($packageJson.version)"
    Write-Host "Scripts available: $($packageJson.scripts.PSObject.Properties.Name -join ', ')"
    Write-Host "Dependencies: $($packageJson.dependencies.PSObject.Properties.Count)"
    Write-Host "Dev Dependencies: $($packageJson.devDependencies.PSObject.Properties.Count)"
} catch {
    Write-Host "❌ Package.json parsing failed: $($_.Exception.Message)"
}

# 8) Configuration Files Check
Write-Host "`nStep 8: Configuration Files Check"
Write-Host "---------------------------------------"
$configFiles = @(
    "next.config.js",
    "tailwind.config.js", 
    "tsconfig.json",
    "postcss.config.js"
)

foreach ($file in $configFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "✅ $file ($size bytes)"
    } else {
        Write-Host "❌ $file - MISSING"
    }
}

# 9) Summary & Recommendations
Write-Host "`nAdmin Panel Test Summary"
Write-Host "============================"

Write-Host "`nNext Steps:"
Write-Host "   1. Start admin dashboard: npm run dev"
Write-Host "   2. Test login functionality"
Write-Host "   3. Navigate through each page systematically"
Write-Host "   4. Check console for errors and warnings"
Write-Host "   5. Test API connectivity to backend"

Write-Host "`nPriority Fixes:"
Write-Host "   1. Replace deprecated auth functions"
Write-Host "   2. Fix API endpoint mismatches"
Write-Host "   3. Resolve CORS issues"
Write-Host "   4. Update error handling"

Pop-Location
Write-Host "`n== Admin Panel comprehensive test completed =="
