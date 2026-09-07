$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $root "backend"
$frontendPath = Join-Path $root "frontend"
$venvPython = Join-Path $root "venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    $python = $venvPython
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $python = (Get-Command python).Source
} else {
    throw "Python was not found. Install Python 3.11+ and run this script again."
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm was not found. Install Node.js and run this script again."
}

if (-not (Test-Path (Join-Path $root "venv"))) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    & python -m venv (Join-Path $root "venv")
    if ($LASTEXITCODE -ne 0) { throw "Could not create the Python virtual environment." }
    $python = $venvPython
}

Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
& $python -m pip install -r (Join-Path $backendPath "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Backend dependency installation failed." }

if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    Push-Location $frontendPath
    try {
        & npm install
        if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed." }
    } finally {
        Pop-Location
    }
}

$backend = $null
$frontend = $null

try {
    Write-Host "Starting backend at http://127.0.0.1:8000 ..." -ForegroundColor Green
    $backend = Start-Process -FilePath $python `
        -ArgumentList @("-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload") `
        -WorkingDirectory $root -NoNewWindow -PassThru

    Write-Host "Starting frontend at http://localhost:5173 ..." -ForegroundColor Green
    $frontend = Start-Process -FilePath "npm.cmd" `
        -ArgumentList @("run", "dev") `
        -WorkingDirectory $frontendPath -NoNewWindow -PassThru

    Write-Host "Press Ctrl+C to stop both services." -ForegroundColor Yellow
    while (-not $backend.HasExited -and -not $frontend.HasExited) {
        Start-Sleep -Seconds 1
    }
} finally {
    foreach ($process in @($frontend, $backend)) {
        if ($null -ne $process -and -not $process.HasExited) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    }
}