# PrimeGuard Windows PowerShell 5.1+ launcher. No activation required.
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

function Invoke-CheckedPython {
    param([string[]]$Arguments)
    & $script:venvPython @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Python command failed (exit $LASTEXITCODE): $($Arguments -join ' ')" }
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "[1/4] Creating isolated Python environment..." -ForegroundColor Cyan
    $candidates = @(
        @{ File = "py"; Args = @("-3.11", "-m", "venv", ".venv") },
        @{ File = "py"; Args = @("-3", "-m", "venv", ".venv") },
        @{ File = "python"; Args = @("-m", "venv", ".venv") }
    )
    $created = $false
    foreach ($candidate in $candidates) {
        if (-not (Get-Command $candidate.File -ErrorAction SilentlyContinue)) { continue }
        & $candidate.File @($candidate.Args)
        if ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $venvPython)) {
            $created = $true
            break
        }
    }
    if (-not $created) {
        throw "Could not create .venv. Install Python 3.11, verify 'py -3.11 --version', and ensure this folder is writable."
    }
}
if (-not (Test-Path -LiteralPath $venvPython)) { throw "Virtual environment Python was not found: $venvPython" }

Write-Host "[2/4] Installing dependencies..." -ForegroundColor Cyan
Invoke-CheckedPython @("-m", "pip", "install", "-r", "requirements.txt")

Write-Host "[3/4] Running automated tests..." -ForegroundColor Cyan
Invoke-CheckedPython @("-m", "compileall", "-q", "app.py", "core", "analytics")
Invoke-CheckedPython @("-m", "pytest", "-q")

Write-Host "[4/4] Starting PrimeGuard..." -ForegroundColor Green
Write-Host "Open http://localhost:8501 if your browser does not open automatically." -ForegroundColor Green
Invoke-CheckedPython @("-m", "streamlit", "run", "app.py", "--server.address", "127.0.0.1", "--server.port", "8501")
