#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Creating virtual environment in .venv ..."
python3 -m venv .venv

echo "Installing dependencies ..."
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo ""
echo "Setup complete."
echo "Activate with: source .venv/bin/activate"
echo "Next steps:"
echo "  1. Install Ollama: https://ollama.com"
echo "  2. ollama pull qwen2.5:3b"
echo "  3. Copy documents to data/raw/"
echo "  4. python main.py ingest"
