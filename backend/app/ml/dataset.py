import json
from pathlib import Path
from typing import Any, Optional
from datasets import Dataset

from app.ml.config import BIO_DIR, SPLITS_FILE, LABEL2ID, MAX_LENGTH
from app.ml.tokenizer_utils import tokenize_and_align_batch

def load_bio_document(path: Path) -> tuple[list[str], list[str]]:
    """Loads a single .bio tab-separated file and returns (tokens, tags)."""
    tokens: list[str] = []
    tags: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                tokens.append(parts[0])
                tags.append(parts[1])
    return tokens, tags

def chunk_bio_document(
    tokens: list[str],
    tags: list[str],
    chunk_size: int = 120,
    overlap: int = 20,
) -> list[tuple[list[str], list[str]]]:
    """Splits a long token sequence into overlapping chunks for transformer input."""
    if len(tokens) <= chunk_size:
        return [(tokens, tags)]

    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(tokens), step):
        end = min(start + chunk_size, len(tokens))
        chunks.append((tokens[start:end], tags[start:end]))
        if end >= len(tokens):
            break
    return chunks

def load_split_data(
    split_name: str,
    bio_dir: Optional[Path] = None,
    splits_file: Optional[Path] = None,
    chunk_size: int = 120,
    overlap: int = 20,
) -> dict[str, list[list[str]]]:
    """Loads tokens and tags for all resumes in a given split (train, val, or test)."""
    bio_dir = bio_dir or BIO_DIR
    splits_file = splits_file or SPLITS_FILE

    with open(splits_file, "r", encoding="utf-8") as f:
        splits = json.load(f)

    resume_ids = splits.get(split_name, [])
    all_chunks_tokens: list[list[str]] = []
    all_chunks_tags: list[list[str]] = []

    for resume_id in resume_ids:
        bio_path = bio_dir / f"{resume_id}.bio"
        if not bio_path.exists():
            continue
        tokens, tags = load_bio_document(bio_path)
        chunks = chunk_bio_document(tokens, tags, chunk_size=chunk_size, overlap=overlap)
        for c_tokens, c_tags in chunks:
            if c_tokens:
                all_chunks_tokens.append(c_tokens)
                all_chunks_tags.append(c_tags)

    return {"tokens": all_chunks_tokens, "ner_tags": all_chunks_tags}

def create_hf_dataset(
    split_name: str,
    tokenizer: Any,
    bio_dir: Optional[Path] = None,
    splits_file: Optional[Path] = None,
    label2id: Optional[dict[str, int]] = None,
    max_length: int = MAX_LENGTH,
) -> Dataset:
    """Creates a tokenized and label-aligned HuggingFace Dataset for a split."""
    label2id = label2id or LABEL2ID
    raw_data = load_split_data(split_name, bio_dir=bio_dir, splits_file=splits_file)

    raw_dataset = Dataset.from_dict(raw_data)
    aligned_dataset = raw_dataset.map(
        lambda batch: tokenize_and_align_batch(
            batch,
            tokenizer=tokenizer,
            label2id=label2id,
            max_length=max_length,
        ),
        batched=True,
    )
    return aligned_dataset
