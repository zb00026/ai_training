"""Verify the project is ready for fully offline use."""

import shutil
import subprocess
from pathlib import Path
from typing import Any


def check_offline_ready(config: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []

    if not config.get("offline", {}).get("enabled", False):
        errors.append("Set offline.enabled: true in config/config.yaml")

    base_local = root / config["models"]["base_hf_local"]
    if not (base_local / "config.json").exists():
        errors.append(f"Missing base model: {base_local} (run download-models online once)")

    emb_local = root / config["models"]["embedding_local"]
    if not emb_local.exists():
        errors.append(f"Missing embedding model: {emb_local}")

    venv_python = root / ".venv" / "Scripts" / "python.exe"
    venv_python_unix = root / ".venv" / "bin" / "python"
    wheels = root / "wheels"
    if not venv_python.exists() and not venv_python_unix.exists() and not wheels.exists():
        errors.append("Missing .venv or wheels/ — copy venv or run setup-offline.ps1")

    if shutil.which("ollama") is None:
        errors.append("Ollama not found in PATH — install Ollama on this machine")

    base_ollama = config["ollama"]["base_model"]
    try:
        result = subprocess.run(
            ["ollama", "show", base_ollama],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            errors.append(
                f"Ollama model '{base_ollama}' not found — run: ollama pull {base_ollama}"
            )
    except FileNotFoundError:
        pass

    return errors
