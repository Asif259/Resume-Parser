from pathlib import Path
import pytest
from transformers import AutoTokenizer

from app.ml.config import ALL_LABELS, LABEL2ID, ID2LABEL
from app.ml.tokenizer_utils import align_labels_with_tokens, tokenize_and_align_batch
from app.ml.dataset import load_bio_document, chunk_bio_document, load_split_data
from app.ml.evaluate import compute_metrics

def test_labels_and_mapping():
    assert len(ALL_LABELS) == 23
    assert ALL_LABELS[0] == "O"
    assert "B-PERSON_NAME" in ALL_LABELS
    assert "I-PERSON_NAME" in ALL_LABELS
    assert LABEL2ID["O"] == 0
    assert ID2LABEL[0] == "O"

def test_align_labels_with_tokens_single_and_subwords():
    # Simulated word_ids: [None, 0, 1, 1, 2, None] -> [CLS], Word0, Word1_part1, Word1_part2, Word2, [SEP]
    labels = ["B-PERSON_NAME", "B-JOB_TITLE", "O"]
    word_ids = [None, 0, 1, 1, 2, None]

    aligned = align_labels_with_tokens(labels, word_ids, LABEL2ID, label_all_subwords=True)

    assert aligned[0] == -100  # [CLS]
    assert aligned[1] == LABEL2ID["B-PERSON_NAME"]
    assert aligned[2] == LABEL2ID["B-JOB_TITLE"]
    assert aligned[3] == LABEL2ID["I-JOB_TITLE"]  # Subword converted to I-
    assert aligned[4] == LABEL2ID["O"]
    assert aligned[5] == -100  # [SEP]

def test_align_labels_without_all_subwords():
    labels = ["B-PERSON_NAME", "B-JOB_TITLE", "O"]
    word_ids = [None, 0, 1, 1, 2, None]

    aligned = align_labels_with_tokens(labels, word_ids, LABEL2ID, label_all_subwords=False)

    assert aligned[0] == -100
    assert aligned[1] == LABEL2ID["B-PERSON_NAME"]
    assert aligned[2] == LABEL2ID["B-JOB_TITLE"]
    assert aligned[3] == -100  # Ignored when label_all_subwords=False
    assert aligned[4] == LABEL2ID["O"]
    assert aligned[5] == -100

def test_chunk_bio_document():
    tokens = [f"tok_{i}" for i in range(50)]
    tags = ["O"] * 50

    chunks = chunk_bio_document(tokens, tags, chunk_size=20, overlap=5)
    assert len(chunks) == 3
    assert len(chunks[0][0]) == 20
    assert chunks[0][0][0] == "tok_0"
    assert chunks[1][0][0] == "tok_15"  # 20 - 5 = 15
    assert chunks[2][0][0] == "tok_30"
    assert chunks[2][0][-1] == "tok_49"

def test_load_split_data():
    fixtures_dir = Path(__file__).resolve().parent / "fixtures"
    bio_dir = fixtures_dir / "bio"
    splits_file = fixtures_dir / "splits.json"

    train_data = load_split_data("train", bio_dir=bio_dir, splits_file=splits_file)
    assert "tokens" in train_data
    assert "ner_tags" in train_data
    assert len(train_data["tokens"]) > 0
    assert len(train_data["ner_tags"]) == len(train_data["tokens"])

def test_compute_metrics():
    # 2 samples, 3 tokens each
    # Sample 0: true: [B-PERSON_NAME, I-PERSON_NAME, O]
    # Sample 1: true: [B-COMPANY, O, O]
    p_name_b = LABEL2ID["B-PERSON_NAME"]
    p_name_i = LABEL2ID["I-PERSON_NAME"]
    comp_b = LABEL2ID["B-COMPANY"]
    o_idx = LABEL2ID["O"]

    labels = [
        [p_name_b, p_name_i, o_idx],
        [comp_b, o_idx, -100],
    ]
    # Perfect predictions: logits shape (2, 3, 23)
    import numpy as np
    logits = np.zeros((2, 3, len(ALL_LABELS)))
    logits[0, 0, p_name_b] = 10.0
    logits[0, 1, p_name_i] = 10.0
    logits[0, 2, o_idx] = 10.0
    logits[1, 0, comp_b] = 10.0
    logits[1, 1, o_idx] = 10.0

    metrics = compute_metrics((logits, labels), id2label=ID2LABEL)
    assert metrics["f1"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
