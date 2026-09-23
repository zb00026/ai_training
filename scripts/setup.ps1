# Create portable venv in project root
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Creating virtual environment in .venv ..."
python -m venv .venv

Write-Host "Installing dependencies ..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements.txt

Write-Host ""
Write-Host "Setup complete."
Write-Host "Activate with: .\.venv\Scripts\Activate.ps1"
Write-Host "Next steps:"
Write-Host "  1. Install Ollama: https://ollama.com"
Write-Host "  2. ollama pull qwen2.5:3b"
Write-Host "  3. Copy documents to data\raw\"
Write-Host "  4. python main.py ingest"
