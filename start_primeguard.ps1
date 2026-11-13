# PrimeGuard one-command Windows setup and launch.
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "[1/4] Creating isolated Python environment..." -ForegroundColor Cyan
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Python virtual environment could not be created. Check that Python is installed." }
}

Write-Host "[2/4] Installing project dependencies..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
& $venvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed. Check your internet connection and requirements.txt." }

Write-Host "[3/4] Running automated tests..." -ForegroundColor Cyan
& $venvPython -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed. Copy the full error output and share it for diagnosis." }

Write-Host "[4/4] Starting PrimeGuard..." -ForegroundColor Green
Write-Host "The app will open at http://localhost:8501" -ForegroundColor Green
& $venvPython -m streamlit run app.py
if ($LASTEXITCODE -ne 0) { throw "Streamlit stopped with an error." }
