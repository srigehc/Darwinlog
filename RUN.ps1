# Darwin Log Compare - Auto Setup & Run (PowerShell)
# Right-click on this file and select "Run with PowerShell"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Darwin Log Compare - Auto Setup & Run" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set error action preference
$ErrorActionPreference = "Continue"

# Check if Python is installed
try {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
    $pythonVersion = & $pythonExe --version 2>&1
    Write-Host "✓ Found Python: $pythonVersion" -ForegroundColor Green
    Write-Host "  Location: $pythonExe" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}

# Change to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "✓ Working directory: $scriptDir" -ForegroundColor Green

# Run the setup and execution script
Write-Host ""
Write-Host "Launching Darwin Log Compare..." -ForegroundColor Cyan
Write-Host ""

& $pythonExe setup_and_run.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Pipeline execution failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check that all input log files exist:" -ForegroundColor Yellow
    Write-Host "   - SystemLog.csv" -ForegroundColor Gray
    Write-Host "   - hl7Log.txt" -ForegroundColor Gray
    Write-Host "   - sbxLog.xml" -ForegroundColor Gray
    Write-Host "   - DoComLog.txt" -ForegroundColor Gray
    Write-Host "2. Ensure at least 500MB free disk space" -ForegroundColor Yellow
    Write-Host "3. Try running again with Administrator privileges" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host ""
Write-Host "SUCCESS! Press Enter to close this window..." -ForegroundColor Green
Read-Host
exit 0
