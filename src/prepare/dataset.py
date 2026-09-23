import json
from pathlib import Path
from typing import Any


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return [c for c in chunks if c]


def build_training_dataset(config: dict[str, Any], root: Path) -> Path:
    """Build instruction-tuning JSONL from processed text chunks."""
    processed_dir = root / config["ingest"]["processed_dir"]
    training_dir = root / config["prepare"]["training_dir"]
    training_dir.mkdir(parents=True, exist_ok=True)

    chunk_size = config["prepare"]["chunk_size"]
    overlap = config["prepare"]["chunk_overlap"]
    out_path = training_dir / "train.jsonl"

    records: list[dict[str, str]] = []
    for txt_path in sorted(processed_dir.rglob("*.txt")):
        text = txt_path.read_text(encoding="utf-8")
        source = str(txt_path.relative_to(processed_dir))
        for i, chunk in enumerate(_chunk_text(text, chunk_size, overlap)):
            records.append(
                {
                    "instruction": f"Summarize and explain the following content from {source}.",
                    "input": chunk,
                    "output": chunk,
                }
            )

    with open(out_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return out_path
