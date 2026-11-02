from typing import Any, Optional

def align_labels_with_tokens(
    labels: list[str],
    word_ids: list[Optional[int]],
    label2id: dict[str, int],
    label_all_subwords: bool = True,
) -> list[int]:
    """Aligns word-level BIO labels to subword tokens produced by a HuggingFace tokenizer.

    Args:
        labels: Original word-level label strings (e.g. ['B-PERSON_NAME', 'I-PERSON_NAME', 'O'])
        word_ids: List of word indices for each token (None for special tokens like [CLS], [SEP])
        label2id: Mapping from label string to integer ID
        label_all_subwords: If True, subwords of B-X get I-X. If False, subwords get -100.

    Returns:
        List of integer label IDs, with -100 for ignored tokens (special tokens or subwords).
    """
    new_labels: list[int] = []
    current_word: Optional[int] = None

    for word_id in word_ids:
        if word_id is None:
            # Special tokens ([CLS], [SEP], [PAD]) are ignored by loss function
            new_labels.append(-100)
        elif word_id != current_word:
            # First subword of word
            current_word = word_id
            label_str = labels[word_id] if word_id < len(labels) else "O"
            new_labels.append(label2id.get(label_str, label2id.get("O", 0)))
        else:
            # Subsequent subwords of the same word
            if label_all_subwords:
                label_str = labels[word_id] if word_id < len(labels) else "O"
                if label_str.startswith("B-"):
                    sub_label = "I-" + label_str[2:]
                    new_labels.append(label2id.get(sub_label, label2id.get("O", 0)))
                else:
                    new_labels.append(label2id.get(label_str, label2id.get("O", 0)))
            else:
                new_labels.append(-100)

    return new_labels

def tokenize_and_align_batch(
    examples: dict[str, list[Any]],
    tokenizer: Any,
    label2id: dict[str, int],
    max_length: int = 256,
    label_all_subwords: bool = True,
) -> dict[str, Any]:
    """Tokenizes a batch of word sequences and aligns their BIO labels."""
    tokenized_inputs = tokenizer(
        examples["tokens"],
        truncation=True,
        is_split_into_words=True,
        max_length=max_length,
        padding="max_length",
    )

    all_aligned_labels = []
    for i, labels in enumerate(examples["ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        aligned = align_labels_with_tokens(
            labels=labels,
            word_ids=word_ids,
            label2id=label2id,
            label_all_subwords=label_all_subwords,
        )
        all_aligned_labels.append(aligned)

    tokenized_inputs["labels"] = all_aligned_labels
    return tokenized_inputs

