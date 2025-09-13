# Zimmer Unified Diagnostics Orchestrator
# Runs backend health checks, port checks, frontend smoke tests, and API endpoint tests

param(
	[string]$BackendUrl = "http://localhost:8000",
	[string]$UserPanelUrl = "http://localhost:3000",
	[string]$AdminPanelUrl = "http://localhost:3001"
)

$ErrorActionPreference = "Stop"

function New-Timestamp {
	(Get-Date).ToString("yyyyMMdd_HHmmss")
}

function Test-Port {
	param(
		[string]$TargetHost,
		[int]$Port
	)
	try {
		$tcp = New-Object System.Net.Sockets.TcpClient
		$iar = $tcp.BeginConnect($TargetHost, $Port, $null, $null)
		$connected = $iar.AsyncWaitHandle.WaitOne(2000, $false)
		if ($connected) { $tcp.EndConnect($iar); $tcp.Close(); return $true } else { $tcp.Close(); return $false }
	} catch { return $false }
}

$timestamp = New-Timestamp
$reportsDir = Join-Path $PSScriptRoot "reports"
if (!(Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir | Out-Null }

$reportPath = Join-Path $reportsDir "unified_diagnostics_$timestamp.md"

$results = @()

Write-Host "🔎 Running unified diagnostics..." -ForegroundColor Yellow

# Precompute URLs
$backendHealthUrl = ($BackendUrl.TrimEnd('/')) + "/health"
$backendCorsUrl = ($BackendUrl.TrimEnd('/')) + "/test-cors"

# 1) Backend health
Write-Host ("`n🩺 Checking backend health {0}" -f $backendHealthUrl) -ForegroundColor Cyan
try {
	$health = Invoke-WebRequest -Uri $backendHealthUrl -UseBasicParsing -TimeoutSec 5
	$results += @{ name = "Backend Health"; status = $health.StatusCode; ok = ($health.StatusCode -eq 200); detail = $health.Content }
} catch {
	$results += @{ name = "Backend Health"; status = "ERROR"; ok = $false; detail = $_.Exception.Message }
}

# 2) CORS test endpoint
Write-Host ("`n🌐 Checking CORS test {0}" -f $backendCorsUrl) -ForegroundColor Cyan
try {
	$cors = Invoke-WebRequest -Uri $backendCorsUrl -UseBasicParsing -TimeoutSec 5
	$results += @{ name = "CORS Test"; status = $cors.StatusCode; ok = ($cors.StatusCode -eq 200); detail = $cors.Content }
} catch {
	$results += @{ name = "CORS Test"; status = "ERROR"; ok = $false; detail = $_.Exception.Message }
}

# 3) Port checks
Write-Host "`n🔌 Checking ports" -ForegroundColor Cyan
$ports = @(
	@{ name = "Backend:8000"; host = "localhost"; port = 8000 },
	@{ name = "User Panel:3000"; host = "localhost"; port = 3000 },
	@{ name = "Admin Panel:3001"; host = "localhost"; port = 3001 }
)
foreach ($p in $ports) {
	$open = Test-Port -TargetHost $p.host -Port $p.port
	$portStatus = if ($open) { "OPEN" } else { "CLOSED" }
	$results += @{ name = "Port $($p.name)"; status = $portStatus; ok = $open; detail = "" }
}

# 4) Frontend smoke test (user panel)
$smokeScript = Join-Path (Join-Path $PSScriptRoot "..") "..\zimmer_user_panel\smoke_test.ps1"
if (Test-Path $smokeScript) {
	Write-Host "`n🧪 Running user panel smoke test" -ForegroundColor Cyan
	try {
		$smokeOutput = powershell -NoProfile -ExecutionPolicy Bypass -File $smokeScript 2>&1 | Out-String
		$results += @{ name = "User Panel Smoke"; status = "RAN"; ok = ($smokeOutput -match "PASS:" -and -not ($smokeOutput -match "FAIL:" -or $smokeOutput -match "ERROR:")); detail = $smokeOutput }
	} catch {
		$results += @{ name = "User Panel Smoke"; status = "ERROR"; ok = $false; detail = $_.Exception.Message }
	}
} else {
	$results += @{ name = "User Panel Smoke"; status = "SKIPPED"; ok = $false; detail = "smoke_test.ps1 not found" }
}

# 5) API endpoint suite (python)
$apiTest = Join-Path (Join-Path $PSScriptRoot "..") "..\scripts\api_endpoint_test.py"
if (Test-Path $apiTest) {
	Write-Host "`n🧰 Running API endpoint tests" -ForegroundColor Cyan
	try {
		$env:PYTHONIOENCODING = "utf-8"
		$apiOutput = python $apiTest 2>&1 | Out-String
		$results += @{ name = "API Endpoint Suite"; status = "RAN"; ok = ($apiOutput -match "Successful:" -and -not ($apiOutput -match "Failed:")); detail = $apiOutput }
	} catch {
		$results += @{ name = "API Endpoint Suite"; status = "ERROR"; ok = $false; detail = $_.Exception.Message }
	}
} else {
	$results += @{ name = "API Endpoint Suite"; status = "SKIPPED"; ok = $false; detail = "scripts/api_endpoint_test.py not found" }
}

# 6) Summarize and write report
$total = $results.Count
$oks = ($results | Where-Object { $_.ok }).Count
$fails = $total - $oks

$md = @()
$md += "# Zimmer Unified Diagnostics Report"
$md += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$md += ""
$md += "## Summary"
$md += "- Total Checks: $total"
$md += "- ✅ OK: $oks"
$md += "- ❌ Issues: $fails"
$md += ""
$md += "## Details"
foreach ($r in $results) {
	$md += "### $($r.name)"
	$md += "- Status: $($r.status)"
	$resultText = if ($r.ok) { "OK" } else { "ISSUE" }
	$md += "- Result: $resultText"
	if ($r.detail) {
		$md += "- Output:"
		$lines = $r.detail -split '\r?\n'
		foreach ($line in $lines) {
			$md += "    $line"
		}
	}
	$md += ""
}

$mdText = ($md -join "`r`n")
$mdText | Out-File -FilePath $reportPath -Encoding utf8

Write-Host ("`n📄 Report saved to: {0}" -f $reportPath) -ForegroundColor Yellow

# Exit with non-zero if any issues
if ($fails -gt 0) { exit 1 } else { exit 0 }
