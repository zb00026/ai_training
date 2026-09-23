# Download HuggingFace models into models/cache/ (run once while online)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Downloading Qwen2.5-3B-Instruct + embedding model (no HuggingFace login required)."
Write-Host ""

& .\.venv\Scripts\python.exe main.py download-models
