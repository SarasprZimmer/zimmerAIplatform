# Comprehensive API Endpoints Test
# Tests all backend API endpoints including new discount system

$ErrorActionPreference = "Stop"

Write-Host "🔍 Zimmer Backend API Endpoints Comprehensive Test" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""

# Test Results
$testResults = @()

function Add-TestResult {
    param(
        [string]$Endpoint,
        [string]$Method,
        [string]$Status,
        [string]$Details
    )
    $testResults += [PSCustomObject]@{
        Endpoint = $Endpoint
        Method = $Method
        Status = $Status
        Details = $Details
        Timestamp = Get-Date
    }
}

function Write-TestResult {
    param(
        [string]$Endpoint,
        [string]$Method,
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
    
    Write-Host "[$Method] $Endpoint - " -NoNewline
    Write-Host $Status -ForegroundColor $color
    if ($Details) {
        Write-Host "  Details: $Details" -ForegroundColor Gray
    }
    
    Add-TestResult -Endpoint $Endpoint -Method $Method -Status $Status -Details $Details
}

# Get admin token for authenticated tests
Write-Host "🔐 Getting admin authentication token..." -ForegroundColor Cyan
try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email":"admin@zimmer.com","password":"admin123"}'
    $adminToken = $loginResponse.access_token
    $adminHeaders = @{
        "Authorization" = "Bearer $adminToken"
        "Content-Type" = "application/json"
    }
    Write-Host "✅ Admin authentication successful" -ForegroundColor Green
} catch {
    Write-Host "❌ Admin authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Get user token for user-specific tests
Write-Host "🔐 Getting user authentication token..." -ForegroundColor Cyan
try {
    $userLoginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email":"test@example.com","password":"test123"}'
    $userToken = $userLoginResponse.access_token
    $userHeaders = @{
        "Authorization" = "Bearer $userToken"
        "Content-Type" = "application/json"
    }
    Write-Host "✅ User authentication successful" -ForegroundColor Green
} catch {
    Write-Host "❌ User authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    $userHeaders = $null
}

Write-Host ""

# 1. Health and System Endpoints
Write-Host "🏥 Testing Health and System Endpoints..." -ForegroundColor Cyan

$healthEndpoints = @(
    @{ Path = "/docs"; Method = "GET"; Auth = $false },
    @{ Path = "/api/health"; Method = "GET"; Auth = $false },
    @{ Path = "/api/auth/csrf"; Method = "GET"; Auth = $false }
)

foreach ($endpoint in $healthEndpoints) {
    try {
        $headers = if ($endpoint.Auth) { $adminHeaders } else { @{"Content-Type"="application/json"} }
        $response = Invoke-RestMethod -Uri "http://localhost:8000$($endpoint.Path)" -Method $endpoint.Method -Headers $headers -TimeoutSec 10
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "PASS" -Details "Response received"
    } catch {
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "FAIL" -Details $_.Exception.Message
    }
}

# 2. Authentication Endpoints
Write-Host "`n🔐 Testing Authentication Endpoints..." -ForegroundColor Cyan

$authEndpoints = @(
    @{ Path = "/api/auth/login"; Method = "POST"; Body = '{"email":"admin@zimmer.com","password":"admin123"}'; Auth = $false },
    @{ Path = "/api/auth/signup"; Method = "POST"; Body = '{"email":"test@example.com","password":"test123","name":"Test User"}'; Auth = $false },
    @{ Path = "/api/auth/refresh"; Method = "POST"; Auth = $true }
)

foreach ($endpoint in $authEndpoints) {
    try {
        $headers = if ($endpoint.Auth) { $adminHeaders } else { @{"Content-Type"="application/json"} }
        $body = if ($endpoint.Body) { $endpoint.Body } else { $null }
        $response = Invoke-RestMethod -Uri "http://localhost:8000$($endpoint.Path)" -Method $endpoint.Method -Headers $headers -Body $body -TimeoutSec 10
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "PASS" -Details "Authentication successful"
    } catch {
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "FAIL" -Details $_.Exception.Message
    }
}

# 3. Admin Endpoints
Write-Host "`n👑 Testing Admin Endpoints..." -ForegroundColor Cyan

$adminEndpoints = @(
    @{ Path = "/api/admin/users"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/automations"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/payments"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/tickets"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/usage"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/backups"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/notifications"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/fallbacks"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/knowledge"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/kb-templates"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/api-keys"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/tokens/adjustments"; Method = "GET"; Auth = $true }
)

foreach ($endpoint in $adminEndpoints) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000$($endpoint.Path)" -Method $endpoint.Method -Headers $adminHeaders -TimeoutSec 10
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "PASS" -Details "Admin endpoint accessible"
    } catch {
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "FAIL" -Details $_.Exception.Message
    }
}

# 4. Discount System Endpoints
Write-Host "`n🎫 Testing Discount System Endpoints..." -ForegroundColor Cyan

$discountEndpoints = @(
    @{ Path = "/api/admin/discounts"; Method = "GET"; Auth = $true },
    @{ Path = "/api/admin/discounts"; Method = "POST"; Body = '{"code":"TEST20","percent_off":20,"active":true,"automation_ids":[]}'; Auth = $true },
    @{ Path = "/api/discounts/validate"; Method = "POST"; Body = '{"code":"TEST20","automation_id":1,"amount":10000}'; Auth = $false }
)

foreach ($endpoint in $discountEndpoints) {
    try {
        $headers = if ($endpoint.Auth) { $adminHeaders } else { @{"Content-Type"="application/json"} }
        $body = if ($endpoint.Body) { $endpoint.Body } else { $null }
        $response = Invoke-RestMethod -Uri "http://localhost:8000$($endpoint.Path)" -Method $endpoint.Method -Headers $headers -Body $body -TimeoutSec 10
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "PASS" -Details "Discount endpoint working"
    } catch {
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "FAIL" -Details $_.Exception.Message
    }
}

# 5. Payment Endpoints
Write-Host "`n💳 Testing Payment Endpoints..." -ForegroundColor Cyan

$paymentEndpoints = @(
    @{ Path = "/api/payments/zarinpal/init"; Method = "POST"; Body = '{"automation_id":1,"tokens":10}'; Auth = $true },
    @{ Path = "/api/payments/zarinpal/callback"; Method = "GET"; Auth = $false }
)

foreach ($endpoint in $paymentEndpoints) {
    try {
        $headers = if ($endpoint.Auth) { $adminHeaders } else { @{"Content-Type"="application/json"} }
        $body = if ($endpoint.Body) { $endpoint.Body } else { $null }
        $response = Invoke-RestMethod -Uri "http://localhost:8000$($endpoint.Path)" -Method $endpoint.Method -Headers $headers -Body $body -TimeoutSec 10
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "PASS" -Details "Payment endpoint accessible"
    } catch {
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "FAIL" -Details $_.Exception.Message
    }
}

# 6. User Panel Endpoints (if user token available)
if ($userHeaders) {
    Write-Host "`n👥 Testing User Panel Endpoints..." -ForegroundColor Cyan
    
    $userEndpoints = @(
        @{ Path = "/api/me"; Method = "GET"; Auth = $true },
        @{ Path = "/api/automations"; Method = "GET"; Auth = $true },
        @{ Path = "/api/user-automations"; Method = "GET"; Auth = $true },
        @{ Path = "/api/tickets"; Method = "GET"; Auth = $true },
        @{ Path = "/api/notifications"; Method = "GET"; Auth = $true }
    )
    
    foreach ($endpoint in $userEndpoints) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000$($endpoint.Path)" -Method $endpoint.Method -Headers $userHeaders -TimeoutSec 10
            Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "PASS" -Details "User endpoint accessible"
        } catch {
            Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "FAIL" -Details $_.Exception.Message
        }
    }
} else {
    Write-Host "`n👥 Skipping User Panel Endpoints (no user token)" -ForegroundColor Yellow
}

# 7. 2FA and Security Endpoints
Write-Host "`n🔒 Testing 2FA and Security Endpoints..." -ForegroundColor Cyan

$securityEndpoints = @(
    @{ Path = "/api/auth/2fa/initiate"; Method = "POST"; Auth = $true },
    @{ Path = "/api/auth/2fa/activate"; Method = "POST"; Body = '{"secret":"test","code":"123456"}'; Auth = $true },
    @{ Path = "/api/auth/2fa/disable"; Method = "POST"; Auth = $true },
    @{ Path = "/api/auth/verify-email"; Method = "POST"; Body = '{"token":"test"}'; Auth = $false }
)

foreach ($endpoint in $securityEndpoints) {
    try {
        $headers = if ($endpoint.Auth) { $adminHeaders } else { @{"Content-Type"="application/json"} }
        $body = if ($endpoint.Body) { $endpoint.Body } else { $null }
        $response = Invoke-RestMethod -Uri "http://localhost:8000$($endpoint.Path)" -Method $endpoint.Method -Headers $headers -Body $body -TimeoutSec 10
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "PASS" -Details "Security endpoint accessible"
    } catch {
        Write-TestResult -Endpoint $endpoint.Path -Method $endpoint.Method -Status "FAIL" -Details $_.Exception.Message
    }
}

# Generate Summary Report
Write-Host "`n📊 API Endpoints Test Results Summary" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow

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
    Write-Host "[$($result.Method)] $($result.Endpoint): $($result.Status)" -ForegroundColor $color
}

# Overall API Status
Write-Host "`n🎯 Overall API Status:" -ForegroundColor Cyan
if ($failCount -eq 0 -and $errorCount -eq 0) {
    Write-Host "🎉 EXCELLENT! All API endpoints are working correctly!" -ForegroundColor Green
} elseif ($failCount -eq 0) {
    Write-Host "✅ GOOD! No critical API failures, but some errors to investigate." -ForegroundColor Yellow
} else {
    Write-Host "⚠️ ATTENTION NEEDED! Some API endpoints are failing. Check the details above." -ForegroundColor Red
}

Write-Host "`n🚀 API Endpoints Test completed at $(Get-Date)" -ForegroundColor Green
