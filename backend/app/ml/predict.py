from pathlib import Path
from typing import Any, Optional
import torch
import torch.nn.functional as F
from transformers import AutoModelForTokenClassification, AutoTokenizer

from app.ml.config import MODEL_DIR, ID2LABEL, get_device

_MODEL_CACHE: dict[str, tuple[Any, Any]] = {}

def get_ner_model_and_tokenizer(model_dir: Optional[Path] = None) -> tuple[Optional[Any], Optional[Any]]:
    """Loads and caches the fine-tuned token classification model and tokenizer."""
    model_dir = model_dir or MODEL_DIR
    cache_key = str(model_dir)

    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    if not model_dir.exists() or not (model_dir / "config.json").exists():
        return None, None

    device = get_device()
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForTokenClassification.from_pretrained(str(model_dir))
    model.to(device)
    model.eval()

    _MODEL_CACHE[cache_key] = (model, tokenizer)
    return model, tokenizer

def predict_entities(
    text: str,
    model_dir: Optional[Path] = None,
    min_confidence: float = 0.5,
) -> list[dict[str, Any]]:
    """Runs token classification inference on raw text and extracts structured entity spans.

    Returns:
        List of dicts:
        {
            "entity": str,
            "label": str,
            "confidence": float,
            "start": int,
            "end": int
        }
    """
    if not text or not text.strip():
        return []

    model, tokenizer = get_ner_model_and_tokenizer(model_dir)
    if model is None or tokenizer is None:
        return []

    device = next(model.parameters()).device

    # Tokenize with char offset mapping
    inputs = tokenizer(
        text,
        return_offsets_mapping=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )

    offset_mapping = inputs.pop("offset_mapping")[0].tolist()
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits[0]  # (seq_len, num_labels)
        probs = F.softmax(logits, dim=-1)
        confidences, pred_ids = torch.max(probs, dim=-1)

    id2label = model.config.id2label

    # Group BIO tokens into entity spans
    entities: list[dict[str, Any]] = []
    current_entity: Optional[dict[str, Any]] = None

    for idx, (token_conf, pred_id, (start_char, end_char)) in enumerate(
        zip(confidences.tolist(), pred_ids.tolist(), offset_mapping)
    ):
        # Ignore special tokens
        if start_char == end_char:
            if current_entity:
                entities.append(current_entity)
                current_entity = None
            continue

        raw_tag = id2label.get(pred_id, id2label.get(str(pred_id), "O"))

        if raw_tag == "O":
            if current_entity:
                entities.append(current_entity)
                current_entity = None
            continue

        prefix, entity_type = raw_tag[:2], raw_tag[2:]

        if prefix == "B-":
            if current_entity:
                entities.append(current_entity)
            current_entity = {
                "entity": text[start_char:end_char],
                "label": entity_type,
                "confidence": token_conf,
                "start": start_char,
                "end": end_char,
                "token_confidences": [token_conf],
            }
        elif prefix == "I-":
            if current_entity and current_entity["label"] == entity_type:
                # Extend current entity
                current_entity["end"] = end_char
                current_entity["entity"] = text[current_entity["start"]:end_char]
                current_entity["token_confidences"].append(token_conf)
                current_entity["confidence"] = min(current_entity["token_confidences"])
            else:
                if current_entity:
                    entities.append(current_entity)
                current_entity = {
                    "entity": text[start_char:end_char],
                    "label": entity_type,
                    "confidence": token_conf,
                    "start": start_char,
                    "end": end_char,
                    "token_confidences": [token_conf],
                }

    if current_entity:
        entities.append(current_entity)

    # Filter by minimum confidence and clean output dict
    results = []
    for ent in entities:
        if ent["confidence"] >= min_confidence:
            results.append({
                "entity": ent["entity"].strip(),
                "label": ent["label"],
                "confidence": round(float(ent["confidence"]), 4),
                "start": ent["start"],
                "end": ent["end"],
            })

    return results

