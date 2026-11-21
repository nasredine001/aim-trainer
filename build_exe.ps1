# Build a standalone Windows executable for Aim Trainer.
#
#   python -m pip install -r requirements-dev.txt
#   .\build_exe.ps1
#
# Output: dist\AimTrainer.exe

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

& python --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python was not found. Install Python 3.10+ and try again."
    exit 1
}

& python -c "import PyInstaller" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller is missing. Install the build tools first:"
    Write-Host ""
    Write-Host "    python -m pip install -r requirements-dev.txt"
    exit 1
}

if (-not (Test-Path "assets\icon.ico")) {
    Write-Host "Icon not found, generating it..."
    & python tools\make_icon.py
}

$icon = (Resolve-Path "assets\icon.ico").Path
$versionFile = (Resolve-Path "assets\version_info.txt").Path

Write-Host "Building dist\AimTrainer.exe ..."
& python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name AimTrainer `
    --icon $icon `
    --version-file $versionFile `
    --specpath build `
    main.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed."
    exit 1
}

Write-Host ""
Write-Host "Done: dist\AimTrainer.exe"
