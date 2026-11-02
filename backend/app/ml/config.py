from pathlib import Path
import torch
from tools.annotation_schema import BIO_TAGS

# 23 BIO labels
ALL_LABELS: list[str] = ["O"] + [f"B-{t}" for t in BIO_TAGS] + [f"I-{t}" for t in BIO_TAGS]
LABEL2ID: dict[str, int] = {label: idx for idx, label in enumerate(ALL_LABELS)}
ID2LABEL: dict[int, str] = {idx: label for idx, label in enumerate(ALL_LABELS)}

MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 256
BATCH_SIZE = 4
LEARNING_RATE = 5e-5
NUM_EPOCHS = 10
WARMUP_RATIO = 0.1
WEIGHT_DECAY = 0.01

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
BIO_DIR = FIXTURES_DIR / "bio"
SPLITS_FILE = FIXTURES_DIR / "splits.json"
MODEL_DIR = PROJECT_ROOT / "models" / "ner"

def get_device() -> str:
    """Returns torch device string: 'mps' on Apple Silicon, 'cuda', or 'cpu'."""
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
