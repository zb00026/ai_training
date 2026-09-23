from pathlib import Path
from typing import Any


def export_modelfile(config: dict[str, Any], root: Path) -> Path:
    adapter_dir = root / config["training"]["output_dir"]
    if not adapter_dir.exists():
        raise FileNotFoundError(
            f"Missing adapter at {adapter_dir}. Run: python main.py train"
        )

    base_model = config["ollama"]["base_model"]
    modelfile_path = adapter_dir / "Modelfile"

    content = f"""FROM {base_model}
ADAPTER .

SYSTEM You are a helpful assistant trained on the user's documents.
PARAMETER temperature 0.7
"""
    modelfile_path.write_text(content, encoding="utf-8")
    return modelfile_path
