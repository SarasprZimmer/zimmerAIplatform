# Comprehensive Frontend Components Test
# Tests all frontend components and pages for both admin dashboard and user panel

$ErrorActionPreference = "Stop"

Write-Host "🎨 Zimmer Frontend Components Comprehensive Test" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Test Results
$testResults = @()

function Add-TestResult {
    param(
        [string]$Component,
        [string]$Type,
        [string]$Status,
        [string]$Details
    )
    $testResults += [PSCustomObject]@{
        Component = $Component
        Type = $Type
        Status = $Status
        Details = $Details
        Timestamp = Get-Date
    }
}

function Write-TestResult {
    param(
        [string]$Component,
        [string]$Type,
        [string]$Status,
        [string]$Details
    )
    $color = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    
    Write-Host "[$Type] $Component - " -NoNewline
    Write-Host $Status -ForegroundColor $color
    if ($Details) {
        Write-Host "  Details: $Details" -ForegroundColor Gray
    }
    
    Add-TestResult -Component $Component -Type $Type -Status $Status -Details $Details
}

# 1. Admin Dashboard Components Test
Write-Host "👑 Testing Admin Dashboard Components..." -ForegroundColor Cyan

$adminDashboardPath = "zimmermanagement/zimmer-admin-dashboard"

if (Test-Path $adminDashboardPath) {
    Push-Location $adminDashboardPath
    
    # Core Components
    $adminComponents = @(
        @{ Path = "components/Layout.tsx"; Type = "Component" },
        @{ Path = "components/Sidebar.tsx"; Type = "Component" },
        @{ Path = "components/Topbar.tsx"; Type = "Component" },
        @{ Path = "components/ProtectedRoute.tsx"; Type = "Component" },
        @{ Path = "components/AppErrorBoundary.tsx"; Type = "Component" },
        @{ Path = "components/Toast.tsx"; Type = "Component" },
        @{ Path = "components/LoadingSkeletons.tsx"; Type = "Component" },
        @{ Path = "components/ResponsiveTable.tsx"; Type = "Component" },
        @{ Path = "components/MobileBottomNav.tsx"; Type = "Component" },
        @{ Path = "components/DiscountForm.tsx"; Type = "Component" },
        @{ Path = "contexts/AuthContext.tsx"; Type = "Context" },
        @{ Path = "lib/api.ts"; Type = "Library" },
        @{ Path = "lib/auth.ts"; Type = "Library" },
        @{ Path = "lib/auth-client.ts"; Type = "Library" },
        @{ Path = "lib/keep-alive.ts"; Type = "Library" }
    )
    
    foreach ($component in $adminComponents) {
        if (Test-Path $component.Path) {
            Write-TestResult -Component $component.Path -Type $component.Type -Status "PASS" -Details "File exists"
        } else {
            Write-TestResult -Component $component.Path -Type $component.Type -Status "FAIL" -Details "File missing"
        }
    }
    
    # Pages
    $adminPages = @(
        @{ Path = "pages/_app.tsx"; Type = "Page" },
        @{ Path = "pages/index.tsx"; Type = "Page" },
        @{ Path = "pages/login.tsx"; Type = "Page" },
        @{ Path = "pages/users.tsx"; Type = "Page" },
        @{ Path = "pages/clients.tsx"; Type = "Page" },
        @{ Path = "pages/automations.tsx"; Type = "Page" },
        @{ Path = "pages/user-automations.tsx"; Type = "Page" },
        @{ Path = "pages/payments.tsx"; Type = "Page" },
        @{ Path = "pages/tickets.tsx"; Type = "Page" },
        @{ Path = "pages/usage.tsx"; Type = "Page" },
        @{ Path = "pages/backups.tsx"; Type = "Page" },
        @{ Path = "pages/notifications/index.tsx"; Type = "Page" },
        @{ Path = "pages/knowledge.tsx"; Type = "Page" },
        @{ Path = "pages/kb-templates.tsx"; Type = "Page" },
        @{ Path = "pages/kb-monitoring.tsx"; Type = "Page" },
        @{ Path = "pages/fallbacks.tsx"; Type = "Page" },
        @{ Path = "pages/api-keys.tsx"; Type = "Page" },
        @{ Path = "pages/tokens/adjustments.tsx"; Type = "Page" },
        @{ Path = "pages/discounts/index.tsx"; Type = "Page" },
        @{ Path = "pages/discounts/new.tsx"; Type = "Page" },
        @{ Path = "pages/discounts/[id].tsx"; Type = "Page" },
        @{ Path = "pages/discounts/[id]/redemptions.tsx"; Type = "Page" }
    )
    
    foreach ($page in $adminPages) {
        if (Test-Path $page.Path) {
            Write-TestResult -Component $page.Path -Type $page.Type -Status "PASS" -Details "Page exists"
        } else {
            Write-TestResult -Component $page.Path -Type $page.Type -Status "FAIL" -Details "Page missing"
        }
    }
    
    # Configuration Files
    $adminConfigs = @(
        @{ Path = "package.json"; Type = "Config" },
        @{ Path = "next.config.js"; Type = "Config" },
        @{ Path = "tailwind.config.js"; Type = "Config" },
        @{ Path = "tsconfig.json"; Type = "Config" },
        @{ Path = "postcss.config.js"; Type = "Config" },
        @{ Path = ".env.local.example"; Type = "Config" }
    )
    
    foreach ($config in $adminConfigs) {
        if (Test-Path $config.Path) {
            Write-TestResult -Component $config.Path -Type $config.Type -Status "PASS" -Details "Config file exists"
        } else {
            Write-TestResult -Component $config.Path -Type $config.Type -Status "WARNING" -Details "Config file missing"
        }
    }
    
    # Build Test
    Write-Host "`n🔨 Testing Admin Dashboard Build..." -ForegroundColor Cyan
    try {
        $buildOutput = npm run build 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-TestResult -Component "Admin Dashboard" -Type "Build" -Status "PASS" -Details "Build successful"
        } else {
            Write-TestResult -Component "Admin Dashboard" -Type "Build" -Status "FAIL" -Details "Build failed"
        }
    } catch {
        Write-TestResult -Component "Admin Dashboard" -Type "Build" -Status "ERROR" -Details "Build test error: $($_.Exception.Message)"
    }
    
    Pop-Location
} else {
    Write-TestResult -Component "Admin Dashboard" -Type "Directory" -Status "FAIL" -Details "Admin dashboard directory not found"
}

# 2. User Panel Components Test
Write-Host "`n👥 Testing User Panel Components..." -ForegroundColor Cyan

$userPanelPath = "zimmer_user_panel"

if (Test-Path $userPanelPath) {
    Push-Location $userPanelPath
    
    # Core Components
    $userComponents = @(
        @{ Path = "components/DashboardLayout.tsx"; Type = "Component" },
        @{ Path = "components/Sidebar.tsx"; Type = "Component" },
        @{ Path = "components/Topbar.tsx"; Type = "Component" },
        @{ Path = "components/ProtectedRoute.tsx"; Type = "Component" },
        @{ Path = "components/ClientAuthProvider.tsx"; Type = "Component" },
        @{ Path = "components/TwoFADialog.tsx"; Type = "Component" },
        @{ Path = "components/Toast.tsx"; Type = "Component" },
        @{ Path = "components/DiscountCodeField.tsx"; Type = "Component" },
        @{ Path = "components/PriceSummary.tsx"; Type = "Component" },
        @{ Path = "components/PurchaseModal.tsx"; Type = "Component" },
        @{ Path = "components/PaymentLoading.tsx"; Type = "Component" },
        @{ Path = "components/HeaderAuth.tsx"; Type = "Component" },
        @{ Path = "contexts/AuthContext.tsx"; Type = "Context" },
        @{ Path = "lib/apiClient.ts"; Type = "Library" },
        @{ Path = "lib/auth-client.ts"; Type = "Library" },
        @{ Path = "lib/auth-server.ts"; Type = "Library" },
        @{ Path = "lib/auth.ts"; Type = "Library" },
        @{ Path = "lib/csrf.ts"; Type = "Library" },
        @{ Path = "lib/keep-alive.ts"; Type = "Library" },
        @{ Path = "lib/money.ts"; Type = "Library" },
        @{ Path = "hooks/useAuth.ts"; Type = "Hook" }
    )
    
    foreach ($component in $userComponents) {
        if (Test-Path $component.Path) {
            Write-TestResult -Component $component.Path -Type $component.Type -Status "PASS" -Details "File exists"
        } else {
            Write-TestResult -Component $component.Path -Type $component.Type -Status "FAIL" -Details "File missing"
        }
    }
    
    # Pages
    $userPages = @(
        @{ Path = "pages/_app.tsx"; Type = "Page" },
        @{ Path = "pages/index.tsx"; Type = "Page" },
        @{ Path = "pages/login.tsx"; Type = "Page" },
        @{ Path = "pages/signup.tsx"; Type = "Page" },
        @{ Path = "pages/dashboard.tsx"; Type = "Page" },
        @{ Path = "pages/automations.tsx"; Type = "Page" },
        @{ Path = "pages/payment.tsx"; Type = "Page" },
        @{ Path = "pages/settings.tsx"; Type = "Page" },
        @{ Path = "pages/settings/security.tsx"; Type = "Page" },
        @{ Path = "pages/forgot-password.tsx"; Type = "Page" },
        @{ Path = "pages/reset-password.tsx"; Type = "Page" },
        @{ Path = "pages/verify-email.tsx"; Type = "Page" },
        @{ Path = "pages/test.tsx"; Type = "Page" },
        @{ Path = "pages/automations/[id]/purchase.tsx"; Type = "Page" }
    )
    
    foreach ($page in $userPages) {
        if (Test-Path $page.Path) {
            Write-TestResult -Component $page.Path -Type $page.Type -Status "PASS" -Details "Page exists"
        } else {
            Write-TestResult -Component $page.Path -Type $page.Type -Status "FAIL" -Details "Page missing"
        }
    }
    
    # Configuration Files
    $userConfigs = @(
        @{ Path = "package.json"; Type = "Config" },
        @{ Path = "next.config.js"; Type = "Config" },
        @{ Path = "tailwind.config.js"; Type = "Config" },
        @{ Path = "tsconfig.json"; Type = "Config" },
        @{ Path = "postcss.config.js"; Type = "Config" },
        @{ Path = ".env.local.example"; Type = "Config" }
    )
    
    foreach ($config in $userConfigs) {
        if (Test-Path $config.Path) {
            Write-TestResult -Component $config.Path -Type $config.Type -Status "PASS" -Details "Config file exists"
        } else {
            Write-TestResult -Component $config.Path -Type $config.Type -Status "WARNING" -Details "Config file missing"
        }
    }
    
    # Build Test
    Write-Host "`n🔨 Testing User Panel Build..." -ForegroundColor Cyan
    try {
        $buildOutput = npm run build 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-TestResult -Component "User Panel" -Type "Build" -Status "PASS" -Details "Build successful"
        } else {
            Write-TestResult -Component "User Panel" -Type "Build" -Status "FAIL" -Details "Build failed"
        }
    } catch {
        Write-TestResult -Component "User Panel" -Type "Build" -Status "ERROR" -Details "Build test error: $($_.Exception.Message)"
    }
    
    Pop-Location
} else {
    Write-TestResult -Component "User Panel" -Type "Directory" -Status "FAIL" -Details "User panel directory not found"
}

# 3. Shared Components and Styles
Write-Host "`n🎨 Testing Shared Components and Styles..." -ForegroundColor Cyan

$sharedComponents = @(
    @{ Path = "zimmer_user_panel/styles/globals.css"; Type = "Style" },
    @{ Path = "zimmermanagement/zimmer-admin-dashboard/styles/globals.css"; Type = "Style" },
    @{ Path = "zimmermanagement/zimmer-admin-dashboard/styles/mobile.css"; Type = "Style" }
)

foreach ($component in $sharedComponents) {
    if (Test-Path $component.Path) {
        Write-TestResult -Component $component.Path -Type $component.Type -Status "PASS" -Details "Style file exists"
    } else {
        Write-TestResult -Component $component.Path -Type $component.Type -Status "WARNING" -Details "Style file missing"
    }
}

# Generate Summary Report
Write-Host "`n📊 Frontend Components Test Results Summary" -ForegroundColor Yellow
Write-Host "===========================================" -ForegroundColor Yellow

$passCount = ($testResults | Where-Object { $_.Status -eq "PASS" }).Count
$failCount = ($testResults | Where-Object { $_.Status -eq "FAIL" }).Count
$warningCount = ($testResults | Where-Object { $_.Status -eq "WARNING" }).Count
$errorCount = ($testResults | Where-Object { $_.Status -eq "ERROR" }).Count

Write-Host "✅ PASS: $passCount" -ForegroundColor Green
Write-Host "❌ FAIL: $failCount" -ForegroundColor Red
Write-Host "⚠️ WARNING: $warningCount" -ForegroundColor Yellow
Write-Host "💥 ERROR: $errorCount" -ForegroundColor Red

Write-Host "`n📋 Detailed Results:" -ForegroundColor Yellow
foreach ($result in $testResults) {
    $color = switch ($result.Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    Write-Host "[$($result.Type)] $($result.Component): $($result.Status)" -ForegroundColor $color
}

# Overall Frontend Status
Write-Host "`n🎯 Overall Frontend Status:" -ForegroundColor Cyan
if ($failCount -eq 0 -and $errorCount -eq 0) {
    Write-Host "🎉 EXCELLENT! All frontend components are in place and building successfully!" -ForegroundColor Green
} elseif ($failCount -eq 0) {
    Write-Host "✅ GOOD! No critical component failures, but some warnings to investigate." -ForegroundColor Yellow
} else {
    Write-Host "⚠️ ATTENTION NEEDED! Some frontend components are missing or failing to build." -ForegroundColor Red
}

Write-Host "`n🚀 Frontend Components Test completed at $(Get-Date)" -ForegroundColor Green
