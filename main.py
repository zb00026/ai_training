#!/usr/bin/env python3
"""CLI entry point for AI Model Training."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from config_loader import load_config  # noqa: E402
from ingest.loader import ingest_all  # noqa: E402
from prepare.dataset import build_training_dataset  # noqa: E402
from train.lora import train_lora  # noqa: E402
from download_models import download_models  # noqa: E402
from export.ollama_export import export_modelfile  # noqa: E402
from export.ollama_install import install_to_ollama  # noqa: E402
from offline_check import check_offline_ready  # noqa: E402
from rag.indexer import build_rag_index  # noqa: E402
from rag.query import rag_query  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train or index documents for use with Ollama."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ingest", help="Extract text from documents in data/raw/")
    sub.add_parser("prepare", help="Build training JSONL from processed text")
    sub.add_parser("train", help="LoRA fine-tune (requires GPU)")
    sub.add_parser("export-ollama", help="Generate Ollama Modelfile from adapter")
    sub.add_parser(
        "install-ollama",
        help="Create trained model in Ollama app (ollama create)",
    )
    sub.add_parser(
        "check-offline",
        help="Verify project is ready for offline train + Ollama install",
    )
    sub.add_parser(
        "download-models",
        help="Download HuggingFace models to models/cache/ (run once while online)",
    )
    sub.add_parser("rag-index", help="Build vector index for RAG")
    q = sub.add_parser("rag-query", help="Query documents via RAG + Ollama")
    q.add_argument("question", type=str, help="Your question")

    args = parser.parse_args()
    config = load_config(ROOT / "config" / "config.yaml")

    if args.command == "ingest":
        count = ingest_all(config, ROOT)
        print(f"Ingested {count} file(s) -> {config['ingest']['processed_dir']}/")
    elif args.command == "prepare":
        path = build_training_dataset(config, ROOT)
        print(f"Training dataset written to {path}")
    elif args.command == "train":
        train_lora(config, ROOT)
    elif args.command == "export-ollama":
        path = export_modelfile(config, ROOT)
        name = config["ollama"]["trained_model_name"]
        print(f"Modelfile written to {path}")
        print(f"Run: python main.py install-ollama")
        print(f"  or: ollama create {name} -f {path}")
    elif args.command == "install-ollama":
        install_to_ollama(config, ROOT)
    elif args.command == "check-offline":
        errors = check_offline_ready(config, ROOT)
        if errors:
            print("NOT READY for offline use:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        print("Ready for offline use.")
        print(f"  Ollama base: {config['ollama']['base_model']}")
        print(f"  Trained model name: {config['ollama']['trained_model_name']}")
    elif args.command == "download-models":
        download_models(config, ROOT)
    elif args.command == "rag-index":
        build_rag_index(config, ROOT)
        print(f"RAG index built in {config['rag']['index_dir']}/")
    elif args.command == "rag-query":
        answer = rag_query(config, ROOT, args.question)
        print(answer)


if __name__ == "__main__":
    main()
