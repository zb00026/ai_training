from pathlib import Path
from typing import Any

import chromadb
import ollama
from chromadb.config import Settings
from model_paths import resolve_embedding_model
from sentence_transformers import SentenceTransformer


def rag_query(config: dict[str, Any], root: Path, question: str) -> str:
    rag_cfg = config["rag"]
    index_dir = root / rag_cfg["index_dir"]
    ollama_cfg = config["ollama"]

    model_id, model_kwargs = resolve_embedding_model(config, root)
    embedder = SentenceTransformer(model_id, **model_kwargs)
    client = chromadb.PersistentClient(
        path=str(index_dir),
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_collection("documents")

    query_embedding = embedder.encode([question]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=rag_cfg["top_k"],
    )

    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    context = "\n\n---\n\n".join(
        f"[Source: {src}]\n{chunk}" for src, chunk in zip(sources, chunks)
    )

    prompt = f"""Use the following context to answer the question. If the answer is not in the context, say you don't know.

Context:
{context}

Question: {question}
"""

    client_ollama = ollama.Client(host=ollama_cfg["host"])
    response = client_ollama.chat(
        model=ollama_cfg["base_model"],
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]
