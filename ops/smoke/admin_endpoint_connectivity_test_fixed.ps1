Write-Host "== Admin Dashboard Endpoint Connectivity Test (FIXED) =="
Write-Host "====================================================="

# Configuration
$adminUrl = "http://localhost:3001"
$backendUrl = "http://localhost:8000"
$adminCredentials = @{
    email = "admin@zimmer.com"
    password = "admin123"
}

# Test results storage
$testResults = @{}

# Helper function to test endpoint
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Endpoint,
        [object]$Data = $null,
        [object]$Headers = @{}
    )
    
    try {
        $uri = "$backendUrl$Endpoint"
        $params = @{
            Uri = $uri
            Method = $Method
            Headers = $Headers
            ContentType = "application/json"
        }
        
        if ($Data) {
            $params.Body = $Data | ConvertTo-Json -Depth 10
        }
        
        Write-Host "Testing $Name ($Method $Endpoint)..."
        
        $response = Invoke-RestMethod @params -ErrorAction Stop
        
        $testResults[$Name] = @{
            Status = "SUCCESS"
            Response = $response
            Details = "Endpoint responded successfully"
        }
        
        Write-Host "  SUCCESS" -ForegroundColor Green
        return $true
        
    } catch {
        $errorDetails = $_.Exception.Message
        if ($_.Exception.Response) {
            $errorDetails = "HTTP $($_.Exception.Response.StatusCode): $($_.Exception.Response.StatusDescription)"
        }
        
        $testResults[$Name] = @{
            Status = "FAILED"
            Error = $errorDetails
            Details = "Endpoint failed to respond"
        }
        
        Write-Host "  FAILED: $errorDetails" -ForegroundColor Red
        return $false
    }
}

# Helper function to test authenticated endpoint
function Test-AuthenticatedEndpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Endpoint,
        [object]$Data = $null
    )
    
    $headers = @{
        "Authorization" = "Bearer $accessToken"
        "Content-Type" = "application/json"
    }
    
    Test-Endpoint -Name $Name -Method $Method -Endpoint $Endpoint -Data $Data -Headers $headers
}

# Step 1: Test backend connectivity
Write-Host "`nStep 1: Testing Backend Connectivity"
Write-Host "-------------------------------------"

$backendHealth = Test-Endpoint -Name "Backend Health" -Method "GET" -Endpoint "/docs"
if (-not $backendHealth) {
    Write-Host "Backend is not accessible. Please ensure it's running on $backendUrl" -ForegroundColor Red
    exit 1
}

# Step 2: Test authentication
Write-Host "`nStep 2: Testing Authentication"
Write-Host "-------------------------------"

$loginData = @{
    email = $adminCredentials.email
    password = $adminCredentials.password
}

$authResult = Test-Endpoint -Name "Admin Login" -Method "POST" -Endpoint "/api/auth/login" -Data $loginData

if ($authResult) {
    $accessToken = $testResults["Admin Login"].Response.access_token
    Write-Host "  Access token obtained successfully" -ForegroundColor Green
} else {
    Write-Host "Authentication failed. Cannot proceed with authenticated tests." -ForegroundColor Red
    exit 1
}

# Step 3: Test Core Admin Endpoints (CORRECTED PATHS)
Write-Host "`nStep 3: Testing Core Admin Endpoints (Corrected Paths)"
Write-Host "-------------------------------------------------------"

# User Management
Test-AuthenticatedEndpoint -Name "Get Users" -Method "GET" -Endpoint "/api/admin/users"
Test-AuthenticatedEndpoint -Name "Get User Count" -Method "GET" -Endpoint "/api/admin/users?page_size=1"

# Automation Management
Test-AuthenticatedEndpoint -Name "Get Automations" -Method "GET" -Endpoint "/api/admin/automations"
Test-AuthenticatedEndpoint -Name "Get User Automations" -Method "GET" -Endpoint "/api/admin/user-automations"

# Payment Management (this was failing with 500 error)
Test-AuthenticatedEndpoint -Name "Get Payments" -Method "GET" -Endpoint "/api/admin/payments"

# Ticket Management
Test-AuthenticatedEndpoint -Name "Get Tickets" -Method "GET" -Endpoint "/api/admin/tickets"

# Knowledge Base
Test-AuthenticatedEndpoint -Name "Get Knowledge Base" -Method "GET" -Endpoint "/api/admin/knowledge"

# Token Management
Test-AuthenticatedEndpoint -Name "Get Token Adjustments" -Method "GET" -Endpoint "/api/admin/tokens/adjustments"

# Usage Statistics (CORRECTED - user-specific)
Test-AuthenticatedEndpoint -Name "Get User Usage (User 1)" -Method "GET" -Endpoint "/api/admin/usage/1"

# System Status
Test-AuthenticatedEndpoint -Name "Get System Status" -Method "GET" -Endpoint "/api/admin/system/status"

# Backups
Test-AuthenticatedEndpoint -Name "Get Backups" -Method "GET" -Endpoint "/api/admin/backups"

# Fallbacks
Test-AuthenticatedEndpoint -Name "Get Fallbacks" -Method "GET" -Endpoint "/api/admin/fallbacks"

# KB Templates
Test-AuthenticatedEndpoint -Name "Get KB Templates" -Method "GET" -Endpoint "/api/admin/kb-templates"

# KB Monitoring (CORRECTED PATH - with required automation_id)
Test-AuthenticatedEndpoint -Name "Get KB Status" -Method "GET" -Endpoint "/api/admin/kb-status?automation_id=1"

# Step 4: Test Specific Problem Areas (CORRECTED)
Write-Host "`nStep 4: Testing Problem Areas (Corrected)"
Write-Host "--------------------------------------------"

# Notifications (CORRECTED payload format)
Test-AuthenticatedEndpoint -Name "Send Notification" -Method "POST" -Endpoint "/api/admin/notifications/broadcast" -Data @{
    type = "system"
    title = "Test notification from connectivity test"
    body = "This is a test notification to verify the endpoint works"
}

# Token Usage (CORRECTED - user-specific)
Test-AuthenticatedEndpoint -Name "Get Token Usage (User 1)" -Method "GET" -Endpoint "/api/admin/usage/1"

# Step 5: Test Frontend-Backend Integration
Write-Host "`nStep 5: Testing Frontend-Backend Integration"
Write-Host "----------------------------------------------"

# Test if admin dashboard can reach backend
try {
    $frontendTest = Invoke-WebRequest -Uri "$adminUrl" -Method GET -ErrorAction Stop
    Write-Host "Admin dashboard is accessible on $adminUrl" -ForegroundColor Green
} catch {
    Write-Host "Admin dashboard is not accessible on $adminUrl" -ForegroundColor Red
}

# Step 6: Summary Report
Write-Host "`n====================================================="
Write-Host "ENDPOINT CONNECTIVITY TEST SUMMARY (CORRECTED)"
Write-Host "====================================================="

$totalTests = $testResults.Count
$successfulTests = ($testResults.Values | Where-Object { $_.Status -eq "SUCCESS" }).Count
$failedTests = ($totalTests - $successfulTests)

Write-Host "`nOverall Results:"
Write-Host "  Total Tests: $totalTests"
Write-Host "  Successful: $successfulTests" -ForegroundColor Green
Write-Host "  Failed: $failedTests" -ForegroundColor Red

if ($failedTests -gt 0) {
    Write-Host "`nFailed Endpoints:" -ForegroundColor Red
    foreach ($test in $testResults.GetEnumerator()) {
        if ($test.Value.Status -eq "FAILED") {
            Write-Host "  FAILED $($test.Key): $($test.Value.Error)" -ForegroundColor Red
        }
    }
}

Write-Host "`nRecommendations:"
if ($failedTests -eq 0) {
    Write-Host "  All endpoints are working correctly!" -ForegroundColor Green
} else {
    Write-Host "  Check the following:" -ForegroundColor Yellow
    Write-Host "     - Backend server status and logs"
    Write-Host "     - Database connectivity"
    Write-Host "     - API endpoint implementations"
    Write-Host "     - Authentication middleware"
    Write-Host "     - CORS configuration"
}

Write-Host "`n== Endpoint connectivity test completed =="
