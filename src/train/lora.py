import json
from pathlib import Path
from typing import Any

import torch
from datasets import Dataset
from model_paths import resolve_base_hf_model
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer


def _can_use_4bit() -> bool:
    try:
        import bitsandbytes  # noqa: F401

        return torch.cuda.is_available()
    except ImportError:
        return False


def _load_jsonl(path: Path) -> Dataset:
    rows: list[dict[str, str]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return Dataset.from_list(rows)


def _format_example(row: dict[str, str]) -> str:
    return (
        f"### Instruction:\n{row['instruction']}\n\n"
        f"### Input:\n{row['input']}\n\n"
        f"### Response:\n{row['output']}"
    )


def train_lora(config: dict[str, Any], root: Path) -> None:
    cfg = config["training"]
    train_path = root / config["prepare"]["training_dir"] / "train.jsonl"
    if not train_path.exists():
        raise FileNotFoundError(
            f"Missing {train_path}. Run: python main.py prepare"
        )

    output_dir = root / cfg["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    model_id, model_kwargs = resolve_base_hf_model(config, root)
    print(f"Loading base model from: {model_id}")

    use_4bit = _can_use_4bit()
    use_cuda = torch.cuda.is_available()

    if use_4bit:
        from peft import prepare_model_for_kbit_training
        from transformers import BitsAndBytesConfig

        print("Using 4-bit quantization (GPU + bitsandbytes)")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto",
            **model_kwargs,
        )
        model = prepare_model_for_kbit_training(model)
    elif use_cuda:
        print("Using float16 on GPU (bitsandbytes not available)")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            **model_kwargs,
        )
    else:
        print("Using CPU training (no GPU detected — will be slow, may need 16GB+ RAM)")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            **model_kwargs,
        )

    tokenizer = AutoTokenizer.from_pretrained(model_id, **model_kwargs)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    lora_config = LoraConfig(
        r=cfg["lora_r"],
        lora_alpha=cfg["lora_alpha"],
        lora_dropout=cfg["lora_dropout"],
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    model = get_peft_model(model, lora_config)

    dataset = _load_jsonl(train_path)
    dataset = dataset.map(lambda x: {"text": _format_example(x)})

    training_args = SFTConfig(
        output_dir=str(output_dir / "checkpoints"),
        num_train_epochs=cfg["epochs"],
        per_device_train_batch_size=cfg["batch_size"],
        learning_rate=cfg["learning_rate"],
        logging_steps=10,
        save_strategy="epoch",
        fp16=use_cuda and not use_4bit,
        use_cpu=not use_cuda,
        report_to="none",
        max_length=cfg["max_seq_length"],
        dataset_text_field="text",
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    trainer.train()
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    print(f"Adapter saved to {output_dir}")
