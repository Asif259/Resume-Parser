from typing import Any
import numpy as np
from seqeval.metrics import f1_score, precision_score, recall_score, classification_report

from app.ml.config import ID2LABEL

def compute_metrics(eval_pred: Any, id2label: dict[int, str] = ID2LABEL) -> dict[str, float]:
    """Computes precision, recall, and F1 using seqeval ignoring -100 labels."""
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=2)

    true_predictions: list[list[str]] = [
        [id2label[p] for (p, l) in zip(pred_seq, label_seq) if l != -100]
        for pred_seq, label_seq in zip(predictions, labels)
    ]
    true_labels: list[list[str]] = [
        [id2label[l] for (p, l) in zip(pred_seq, label_seq) if l != -100]
        for pred_seq, label_seq in zip(predictions, labels)
    ]

    # Calculate overall metrics
    precision = precision_score(true_labels, true_predictions, zero_division=0)
    recall = recall_score(true_labels, true_predictions, zero_division=0)
    f1 = f1_score(true_labels, true_predictions, zero_division=0)

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }

def get_detailed_report(true_labels: list[list[str]], true_predictions: list[list[str]]) -> str:
    """Returns detailed entity-level classification report from seqeval."""
    return classification_report(true_labels, true_predictions, zero_division=0)

