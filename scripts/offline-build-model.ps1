# Full offline pipeline: ingest -> prepare -> train -> install in Ollama app
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "Missing .venv — run setup.ps1 (online) or setup-offline.ps1 first."
    exit 1
}

Write-Host "=== Offline model build ==="
Write-Host ""

& $Python main.py check-offline
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "[1/5] Ingest documents ..."
& $Python main.py ingest

Write-Host ""
Write-Host "[2/5] Prepare training data ..."
& $Python main.py prepare

Write-Host ""
Write-Host "[3/5] Train LoRA adapter (GPU recommended) ..."
& $Python main.py train

Write-Host ""
Write-Host "[4/5] Export Modelfile ..."
& $Python main.py export-ollama

Write-Host ""
Write-Host "[5/5] Install model into Ollama app ..."
& $Python main.py install-ollama

Write-Host ""
Write-Host "Complete. Open Ollama app and select your trained model."
