Write-Host "== Zimmer Admin Dashboard Smoke Test =="

# Check if we're in the right directory
if (-not (Test-Path "zimmermanagement/zimmer-admin-dashboard")) {
    Write-Host "❌ Admin dashboard not found. Please run from project root."
    exit 1
}

Push-Location zimmermanagement/zimmer-admin-dashboard

# 0) Check Node.js environment
Write-Host "`n📝 Step 0: Node.js Environment Check"
try {
    node --version
    npm --version
    Write-Host "✅ Node.js environment ready"
} catch {
    Write-Host "❌ Node.js not available"
    exit 1
}

# 1) Install dependencies
Write-Host "`n📝 Step 1: Installing Dependencies"
try {
    npm install
    Write-Host "✅ Dependencies installed"
} catch {
    Write-Host "❌ Failed to install dependencies"
    exit 1
}

# 2) Check for build errors
Write-Host "`n📝 Step 2: Checking for Build Errors"
try {
    npm run build
    Write-Host "✅ Build successful"
} catch {
    Write-Host "❌ Build failed - This indicates there are code issues that need fixing"
}

# 3) Check critical files exist
Write-Host "`n📝 Step 3: Critical Files Check"
$criticalFiles = @(
    "pages/_app.tsx",
    "pages/login.tsx",
    "pages/index.tsx",
    "pages/discounts/index.tsx",
    "pages/discounts/new.tsx",
    "pages/discounts/[id].tsx",
    "pages/discounts/[id]/redemptions.tsx",
    "components/Layout.tsx",
    "components/Sidebar.tsx",
    "components/ProtectedRoute.tsx",
    "components/DiscountForm.tsx",
    "contexts/AuthContext.tsx",
    "lib/api.ts",
    "lib/auth.ts"
)

$missingFiles = @()
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file"
    } else {
        Write-Host "❌ $file - MISSING"
        $missingFiles += $file
    }
}

# 4) Check environment configuration
Write-Host "`n📝 Step 4: Environment Configuration Check"
$envFiles = @(".env.local", ".env", "env.user", "env.corrected")
$envFound = $false

foreach ($envFile in $envFiles) {
    if (Test-Path $envFile) {
        Write-Host "✅ Environment file found: $envFile"
        $envFound = $true
        break
    }
}

if (-not $envFound) {
    Write-Host "⚠️ No environment files found - admin dashboard may not work properly"
}

# 5) Summary
Write-Host "`n📊 Admin Dashboard Smoke Test Summary"
Write-Host "======================================"

if ($missingFiles.Count -eq 0 -and $envFound) {
    Write-Host "🎉 Admin dashboard appears to be in good condition!"
} else {
    Write-Host "⚠️ Admin dashboard has some issues:"
    if ($missingFiles.Count -gt 0) {
        Write-Host "   - Missing $($missingFiles.Count) critical files"
    }
    if (-not $envFound) {
        Write-Host "   - Environment not configured"
    }
}

Write-Host "`n🚀 Next steps:"
Write-Host "   1. Start the admin dashboard: npm run dev"
Write-Host "   2. Test login functionality"
Write-Host "   3. Navigate through key pages"

Pop-Location
Write-Host "`n== Admin Dashboard smoke test completed =="
