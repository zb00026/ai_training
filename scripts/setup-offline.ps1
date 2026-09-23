# Install from local wheels (no internet)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path "wheels")) {
    Write-Host "Missing wheels/ folder. Run .\scripts\pack-offline.ps1 on an online machine first."
    exit 1
}

Write-Host "Creating virtual environment ..."
python -m venv .venv

Write-Host "Installing from wheels/ ..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install --no-index --find-links wheels -r requirements.txt

Write-Host "Offline setup complete."
