import subprocess
from pathlib import Path
from typing import Any

from export.ollama_export import export_modelfile


def install_to_ollama(config: dict[str, Any], root: Path) -> str:
    """Create a custom model in Ollama from the trained LoRA adapter."""
    modelfile_path = export_modelfile(config, root)
    model_name = config["ollama"]["trained_model_name"]
    base_model = config["ollama"]["base_model"]

    print(f"Installing '{model_name}' into Ollama (base: {base_model}) ...")
    result = subprocess.run(
        ["ollama", "create", model_name, "-f", str(modelfile_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(
            f"ollama create failed: {stderr}\n"
            f"Make sure Ollama is running and '{base_model}' is already pulled:\n"
            f"  ollama pull {base_model}"
        )

    print(result.stdout.strip())
    print(f"Done. Use in Ollama app or run: ollama run {model_name}")
    return model_name
