"""Resolve HuggingFace model paths for online vs offline use."""

from pathlib import Path
from typing import Any


def _offline_enabled(config: dict[str, Any]) -> bool:
    return bool(config.get("offline", {}).get("enabled", False))


def resolve_base_hf_model(config: dict[str, Any], root: Path) -> tuple[str, dict[str, Any]]:
    models_cfg = config["models"]
    local_path = root / models_cfg["base_hf_local"]

    if _offline_enabled(config):
        if not local_path.exists():
            raise FileNotFoundError(
                f"Offline mode is on but base model not found at {local_path}.\n"
                "On an online machine, run: python main.py download-models\n"
                "Then copy the whole project folder (including models/cache/) offline."
            )
        return str(local_path), {"local_files_only": True}

    if local_path.exists():
        return str(local_path), {"local_files_only": True}

    return models_cfg["base_hf_hub_id"], {}


def resolve_embedding_model(config: dict[str, Any], root: Path) -> tuple[str, dict[str, Any]]:
    models_cfg = config["models"]
    local_path = root / models_cfg["embedding_local"]

    if _offline_enabled(config):
        if not local_path.exists():
            raise FileNotFoundError(
                f"Offline mode is on but embedding model not found at {local_path}.\n"
                "On an online machine, run: python main.py download-models\n"
                "Then copy the whole project folder (including models/cache/) offline."
            )
        return str(local_path), {"local_files_only": True}

    if local_path.exists():
        return str(local_path), {"local_files_only": True}

    return models_cfg["embedding_hub_id"], {}
