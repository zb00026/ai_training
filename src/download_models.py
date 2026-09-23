"""Download HuggingFace models into models/cache/ for offline use."""

from pathlib import Path
from typing import Any

from huggingface_hub import snapshot_download
from sentence_transformers import SentenceTransformer


def download_models(config: dict[str, Any], root: Path) -> None:
    models_cfg = config["models"]
    base_local = root / models_cfg["base_hf_local"]
    embedding_local = root / models_cfg["embedding_local"]

    base_local.mkdir(parents=True, exist_ok=True)
    embedding_local.mkdir(parents=True, exist_ok=True)

    hub_id = models_cfg["base_hf_hub_id"]
    print(f"Downloading base model: {hub_id}")
    print(f"  -> {base_local}")
    snapshot_download(
        repo_id=hub_id,
        local_dir=str(base_local),
        local_dir_use_symlinks=False,
    )

    emb_hub_id = models_cfg["embedding_hub_id"]
    print(f"Downloading embedding model: {emb_hub_id}")
    print(f"  -> {embedding_local}")
    embedder = SentenceTransformer(emb_hub_id)
    embedder.save(str(embedding_local))

    print("")
    print("Download complete. Models saved under models/cache/")
    print("Set offline.enabled: true in config/config.yaml for fully offline runs.")
