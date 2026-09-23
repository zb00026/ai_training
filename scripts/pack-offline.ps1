# Prepare project folder for copy to offline machine
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".venv")) {
    Write-Host "Run .\scripts\setup.ps1 first."
    exit 1
}

Write-Host "=== Offline pack checklist ==="
Write-Host ""

$missing = @()
if (-not (Test-Path "models\cache\base-model\config.json")) {
    $missing += "models/cache/base-model  (run: python main.py download-models)"
}
if (-not (Test-Path "models\cache\embedding-model")) {
    $missing += "models/cache/embedding-model"
}

if ($missing.Count -gt 0) {
    Write-Host "WARNING — missing items (required for offline train/RAG):"
    $missing | ForEach-Object { Write-Host "  - $_" }
    Write-Host ""
}

Write-Host "Downloading pip wheels to wheels/ ..."
New-Item -ItemType Directory -Force -Path wheels | Out-Null
& .\.venv\Scripts\pip.exe download -r requirements.txt -d wheels

Write-Host ""
Write-Host "=== Copy this ENTIRE folder to the offline PC ==="
Write-Host ""
Write-Host "Required folders/files:"
Write-Host "  .venv/              OR wheels/ + run setup-offline.ps1 on target"
Write-Host "  models/cache/       base + embedding models (~6 GB)"
Write-Host "  data/raw/           your documents"
Write-Host "  config/config.yaml  offline.enabled: true"
Write-Host ""
Write-Host "On offline PC also need:"
Write-Host "  - Python (same version as online machine if copying .venv)"
Write-Host "  - Ollama app with base model pulled: ollama pull qwen2.5:3b"
Write-Host ""
Write-Host "On offline PC run:"
Write-Host "  .\scripts\offline-build-model.ps1"
Write-Host "  OR step by step: ingest -> prepare -> train -> install-ollama"
