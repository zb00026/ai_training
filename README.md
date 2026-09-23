# AI Model Training for Ollama

Train a local model from your documents (TXT, MD, PDF, DOCX, DOC, PPTX, PPT, XLSX, XLS) and use it in **Ollama**.

This project supports **two approaches**:

| Approach | What it does | Best for |
|----------|--------------|----------|
| **LoRA fine-tuning** | Updates model weights on your text | Style, terminology, output format |
| **RAG (Retrieval)** | Embeds documents, retrieves at query time | Large doc sets, factual Q&A |

> **Important:** Ollama runs models — it does not train them. This project trains (or indexes) your data, then exports a model Ollama can load.

---

## Architecture

```
Documents (PDF/DOCX/DOC/PPTX/PPT/XLSX/XLS/TXT)
        │
        ▼
   [1] Ingest ──► raw text files
        │
        ▼
   [2] Prepare ──► training JSONL (LoRA)  OR  vector index (RAG)
        │
        ├── LoRA path ──► [3] Train ──► adapter ──► [4] Export Modelfile ──► ollama create
        │
        └── RAG path ──► embed + ChromaDB ──► query via Ollama API with context
```

---

## Project layout

```
AI_Model_Training/
├── .venv/                  # Python environment (portable)
├── wheels/                 # Offline pip packages (optional)
├── config/
│   └── config.yaml         # All settings
├── data/
│   ├── raw/                # Drop your PDFs, DOCX, TXT here
│   ├── processed/            # Extracted text
│   └── training/             # Generated JSONL for fine-tuning
├── models/
│   ├── adapters/           # LoRA output
│   └── rag/                # ChromaDB index
├── src/                    # Python source code
├── scripts/                # Setup & run scripts
├── requirements.txt
└── main.py                 # CLI entry point
```

---

## Quick start (online machine)

### 1. Setup environment

**Windows (PowerShell):**
```powershell
.\scripts\setup.ps1
```

**Linux/macOS:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Add documents

Copy files into `data/raw/`:
- `.txt`, `.md`
- `.pdf`
- `.docx`, `.doc` (legacy Word — requires LibreOffice)
- `.pptx`, `.ppt` (legacy PowerPoint — requires LibreOffice)
- `.xlsx`, `.xls`

### 3. Choose your path

#### Path A — RAG (recommended to start, works on CPU)

```powershell
.\.venv\Scripts\Activate.ps1
python main.py ingest
python main.py rag-index
python main.py rag-query "What does the document say about X?"
```

Uses Ollama's base model + your document context. No GPU training required.

#### Path B — LoRA fine-tuning (needs NVIDIA GPU)

```powershell
.\.venv\Scripts\Activate.ps1
python main.py ingest
python main.py prepare
python main.py train
python main.py export-ollama
ollama create my-trained-model -f models/adapters/latest/Modelfile
ollama run my-trained-model
```

---

## Offline / portable setup

Copy the **entire project folder** to another machine. Two options:

### Option 1 — Copy `.venv` as-is (same OS + same Python version)

Works if both machines are the same OS (e.g. both Windows x64) and same Python minor version.

```powershell
# On source machine (after setup):
.\scripts\pack-offline.ps1

# Copy the whole AI_Model_Training folder to offline machine
# On offline machine:
.\scripts\setup-offline.ps1
```

### Option 2 — Use `wheels/` folder (more reliable)

On a machine **with internet**:

```powershell
.\.venv\Scripts\Activate.ps1
pip download -r requirements.txt -d wheels
```

Copy project folder (including `wheels/`) to offline machine:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --no-index --find-links=wheels -r requirements.txt
```

### Step 3 — Download AI models (while online)

`train` and `rag-index` need HuggingFace models. Download them once into the project folder:

```powershell
.\scripts\download-models.ps1
# or: python main.py download-models
```

This saves models to `models/cache/` inside the project.

### Step 4 — Enable offline mode

On the offline machine, edit `config/config.yaml`:

```yaml
offline:
  enabled: true
```

With offline mode on, these commands use **only local files** (no internet):

| Command | Internet needed? |
|---------|------------------|
| `ingest` | No — reads local files only |
| `prepare` | No — reads local text only |
| `train` | No — uses `models/cache/base-model` |
| `export-ollama` | No — writes local Modelfile |
| `rag-index` | No — uses `models/cache/embedding-model` |
| `rag-query` | No — local index + local Ollama (`localhost`) |
| `download-models` | Yes — run only while online |

### Offline extras you must also copy or pre-install

| Item | Notes |
|------|-------|
| **Ollama** | Install separately on target machine |
| **Ollama base model** | `ollama pull qwen2.5:3b` while online, or copy `%USERPROFILE%\.ollama\models` |
| **`models/cache/`** | From `download-models` — required for train + rag-index offline |
| **`.venv/` or `wheels/`** | Python dependencies |

---

## Configuration

Edit `config/config.yaml`:

```yaml
offline:
  enabled: false   # set true on offline machines

ollama:
  base_model: "qwen2.5:3b"
  host: "http://localhost:11434"

models:
  base_hf_hub_id: "Qwen/Qwen2.5-3B-Instruct"
  base_hf_local: "models/cache/base-model"
  embedding_hub_id: "sentence-transformers/all-MiniLM-L6-v2"
  embedding_local: "models/cache/embedding-model"
```

---

## Hardware requirements

| Task | Minimum | Recommended |
|------|---------|-------------|
| RAG indexing + query | 8 GB RAM, CPU | 16 GB RAM |
| LoRA fine-tune (3B model) | 8 GB VRAM GPU | 16+ GB VRAM |
| LoRA fine-tune (7B model) | 16 GB VRAM | 24 GB VRAM |

For CPU-only machines, use **RAG** or a very small base model (1B–3B).

---

## CLI reference

```
python main.py download-models # Download HF models to models/cache/ (online, once)
python main.py ingest          # Extract text from data/raw/
python main.py prepare         # Build training JSONL from processed text
python main.py train           # LoRA fine-tune (GPU)
python main.py export-ollama   # Generate Modelfile for Ollama
python main.py rag-index       # Build vector index
python main.py rag-query "..."  # Ask a question using RAG + Ollama
```

---

## How Ollama uses your trained model

### LoRA adapter (Safetensors)

Ollama creates a new model from a Modelfile:

```dockerfile
FROM qwen2.5:3b
ADAPTER .
SYSTEM You are a helpful assistant trained on internal documents.
```

Then: `ollama create my-model -f Modelfile`

### RAG

Ollama runs the **base model**. Your project injects retrieved document chunks into the prompt before calling Ollama's API. The model itself is unchanged; answers are grounded in your files.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ollama: command not found` | Install Ollama from https://ollama.com |
| CUDA out of memory | Reduce `batch_size`, use smaller base model, or use RAG |
| Base model mismatch on export | `ollama.base_model` must match the model used during LoRA training |
| Empty ingest results | Check `data/raw/` has supported files; run `python main.py ingest` and read SKIP messages |
| `.doc` / `.ppt` skipped | Install LibreOffice, or convert files to `.docx` / `.pptx` |
| `401 GatedRepoError` on train | Switch to an open model like Qwen (default), or use `huggingface-cli login` for gated models |
| Network used during train/rag-index | Run `download-models` once online, then set `offline.enabled: true` |
| Offline pip fails | Re-download wheels on a matching OS/Python version |

---

## Next steps

1. Start with **RAG** to validate document ingestion and Q&A quality.
2. If you need the model to *behave* differently (tone, format, jargon), add **LoRA fine-tuning**.
3. Tune `config/config.yaml` chunk sizes and base model for your hardware.
