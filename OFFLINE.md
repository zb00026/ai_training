# Offline Guide — Train a Model & Use in Ollama App

Goal: copy this project to an offline PC (Python + Ollama only), train on your documents, and use the new model in the **Ollama desktop app**.

---

## What you need on the offline PC

| Required | Notes |
|----------|-------|
| **Python** | Same version as online PC if you copy `.venv/` |
| **Ollama app** | With base model already pulled: `qwen2.5:3b` |
| **This project folder** | Copied entirely (see checklist below) |

> **DeepSeek note:** If you also have `deepseek-r1:14b` in Ollama, that is fine for general chat — but **LoRA training uses Qwen** in this project. The trained adapter must attach to `qwen2.5:3b`, not DeepSeek.

---

## Online machine (once, before copy)

```powershell
.\scripts\setup.ps1
python main.py download-models
.\scripts\pack-offline.ps1
```

Put your documents in `data/raw/`.

Ensure `config/config.yaml` has:

```yaml
offline:
  enabled: true

ollama:
  base_model: "qwen2.5:3b"
  trained_model_name: "my-docs-model"
```

---

## Copy to offline PC

Copy the **entire** `AI_Model_Training` folder:

```
AI_Model_Training/
├── .venv/                  ← Python libraries (or use wheels/ + setup-offline.ps1)
├── wheels/                 ← backup if .venv doesn't work on target OS
├── models/cache/           ← Qwen weights + embedding model (~6 GB) REQUIRED
├── data/raw/               ← your PDFs, DOCX, etc.
├── config/config.yaml
└── (all other project files)
```

**Ollama base model** is NOT inside this folder — it must already exist in Ollama on the offline PC (`qwen2.5:3b`).

If `.venv` fails on the offline PC (different OS/Python):

```powershell
python -m venv .venv
.\scripts\setup-offline.ps1
```

---

## Offline PC — build trained model for Ollama app

### Option A — one script

```powershell
cd AI_Model_Training
.\scripts\offline-build-model.ps1
```

### Option B — step by step

```powershell
.\.venv\Scripts\Activate.ps1
python main.py check-offline
python main.py ingest
python main.py prepare
python main.py train
python main.py install-ollama
```

`install-ollama` runs `ollama create my-docs-model` and registers it in the Ollama app.

---

## Use in Ollama app

1. Open **Ollama** desktop app
2. Select **`my-docs-model`** (or whatever you set in `trained_model_name`)
3. Chat — the model uses your LoRA adapter on top of `qwen2.5:3b`

Or in terminal:

```powershell
ollama run my-docs-model
```

---

## Verify offline (no internet)

```powershell
python main.py check-offline
```

All commands below work with **no network** when `offline.enabled: true` and `models/cache/` is present:

| Command | Internet |
|---------|----------|
| ingest | No |
| prepare | No |
| train | No |
| export-ollama | No |
| install-ollama | No (uses local Ollama + `qwen2.5:3b`) |
| rag-index / rag-query | No |

---

## Change the model name in Ollama app

Edit `config/config.yaml`:

```yaml
ollama:
  trained_model_name: "company-docs-v1"
```

Then run `python main.py install-ollama` again.
