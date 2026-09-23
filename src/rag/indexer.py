from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from model_paths import resolve_embedding_model
from sentence_transformers import SentenceTransformer


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def build_rag_index(config: dict[str, Any], root: Path) -> None:
    processed_dir = root / config["ingest"]["processed_dir"]
    index_dir = root / config["rag"]["index_dir"]
    index_dir.mkdir(parents=True, exist_ok=True)

    rag_cfg = config["rag"]
    model_id, model_kwargs = resolve_embedding_model(config, root)
    print(f"Loading embedding model from: {model_id}")
    embedder = SentenceTransformer(model_id, **model_kwargs)

    client = chromadb.PersistentClient(
        path=str(index_dir),
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"},
    )

    ids: list[str] = []
    docs: list[str] = []
    metadatas: list[dict[str, str]] = []

    for txt_path in sorted(processed_dir.rglob("*.txt")):
        text = txt_path.read_text(encoding="utf-8")
        source = str(txt_path.relative_to(processed_dir))
        for i, chunk in enumerate(
            _chunk_text(text, rag_cfg["chunk_size"], rag_cfg["chunk_overlap"])
        ):
            doc_id = f"{source}::{i}"
            ids.append(doc_id)
            docs.append(chunk)
            metadatas.append({"source": source})

    if not docs:
        raise FileNotFoundError(
            f"No processed text in {processed_dir}. Run: python main.py ingest"
        )

    embeddings = embedder.encode(docs, show_progress_bar=True).tolist()
    collection.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)
