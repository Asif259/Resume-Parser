import json
from pathlib import Path
from typing import Any, Optional
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

from app.ml.config import (
    ALL_LABELS,
    LABEL2ID,
    ID2LABEL,
    MODEL_NAME,
    MODEL_DIR,
    NUM_EPOCHS,
    BATCH_SIZE,
    LEARNING_RATE,
    WARMUP_RATIO,
    WEIGHT_DECAY,
    MAX_LENGTH,
)
from app.ml.dataset import create_hf_dataset
from app.ml.evaluate import compute_metrics

def build_model(
    model_name: str = MODEL_NAME,
    num_labels: int = len(ALL_LABELS),
    id2label: Optional[dict[int, str]] = None,
    label2id: Optional[dict[str, int]] = None,
) -> AutoModelForTokenClassification:
    """Builds a token classification model initialized with pretrained weights."""
    id2label = id2label or ID2LABEL
    label2id = label2id or LABEL2ID
    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
    )
    return model

def train_ner_model(
    model_name: str = MODEL_NAME,
    output_dir: Optional[Path] = None,
    num_epochs: int = NUM_EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    max_length: int = MAX_LENGTH,
) -> dict[str, Any]:
    """Fine-tunes the token classification model on resume training data and evaluates on val/test."""
    output_dir = output_dir or MODEL_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = build_model(model_name=model_name)

    train_dataset = create_hf_dataset("train", tokenizer=tokenizer, max_length=max_length)
    val_dataset = create_hf_dataset("val", tokenizer=tokenizer, max_length=max_length)
    test_dataset = create_hf_dataset("test", tokenizer=tokenizer, max_length=max_length)

    training_args = TrainingArguments(
        output_dir=str(output_dir / "checkpoints"),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=num_epochs,
        weight_decay=WEIGHT_DECAY,
        warmup_steps=5,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_steps=10,
        save_total_limit=2,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    train_result = trainer.train()

    # Evaluate on test set
    test_metrics = trainer.evaluate(test_dataset, metric_key_prefix="test")

    # Save final best model and tokenizer
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    summary = {
        "train_loss": train_result.training_loss,
        "test_f1": test_metrics.get("test_f1", 0.0),
        "test_precision": test_metrics.get("test_precision", 0.0),
        "test_recall": test_metrics.get("test_recall", 0.0),
        "num_epochs": num_epochs,
    }
    with open(output_dir / "training_metrics.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary

