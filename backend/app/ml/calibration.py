import json
import math
from pathlib import Path
from typing import Any, Optional, Sequence, Union
import numpy as np
from scipy.optimize import minimize_scalar

from app.ml.config import MODEL_DIR

class ConfidenceCalibrator:
    """Calibrates confidence scores using temperature scaling."""

    def __init__(self, temperature: float = 1.0):
        self.temperature = max(0.01, float(temperature))

    def calibrate(self, raw_confidence: float) -> float:
        """Applies learned temperature scaling to a raw confidence score in [0.0, 1.0]."""
        p = max(1e-5, min(1.0 - 1e-5, float(raw_confidence)))
        # Logit
        logit = math.log(p / (1.0 - p))
        # Scaled logit
        scaled = logit / self.temperature
        # Sigmoid
        calibrated = 1.0 / (1.0 + math.exp(-scaled))
        return round(float(calibrated), 4)

    def calibrate_batch(self, confidences: Sequence[float]) -> list[float]:
        """Calibrates a list of raw confidence scores."""
        return [self.calibrate(c) for c in confidences]

    def fit(self, confidences: Sequence[float], labels: Sequence[bool]) -> float:
        """Optimizes temperature parameter T via negative log-likelihood on validation data."""
        if not confidences or not labels or len(confidences) != len(labels):
            return self.temperature

        confs = np.clip(np.array(confidences, dtype=np.float64), 1e-5, 1.0 - 1e-5)
        y = np.array(labels, dtype=np.float64)
        logits = np.log(confs / (1.0 - confs))

        def nll_loss(t: float) -> float:
            scaled = logits / max(1e-3, t)
            # Numerically stable BCE with logits
            loss = np.maximum(scaled, 0) - scaled * y + np.log(1.0 + np.exp(-np.abs(scaled)))
            return float(np.mean(loss))

        res = minimize_scalar(nll_loss, bounds=(0.1, 5.0), method="bounded")
        if res.success:
            self.temperature = round(float(res.x), 4)

        return self.temperature

    def save(self, path: Union[str, Path] = None) -> None:
        """Saves temperature parameter to JSON."""
        path = Path(path or (MODEL_DIR / "calibration.json"))
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"temperature": self.temperature}, f, indent=2)

    @classmethod
    def load(cls, path: Union[str, Path] = None) -> "ConfidenceCalibrator":
        """Loads temperature parameter from JSON if exists, else defaults to 1.0."""
        path = Path(path or (MODEL_DIR / "calibration.json"))
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(temperature=data.get("temperature", 1.0))
            except Exception:
                return cls(temperature=1.0)
        return cls(temperature=1.0)

def compute_ece(
    confidences: Sequence[float],
    accuracies: Sequence[bool],
    num_bins: int = 10,
) -> float:
    """Computes Expected Calibration Error (ECE).

    ECE = sum_m (|B_m| / N) * |acc(B_m) - conf(B_m)|
    """
    if not confidences or not accuracies or len(confidences) != len(accuracies):
        return 0.0

    confs = np.array(confidences, dtype=np.float64)
    accs = np.array(accuracies, dtype=np.float64)
    n = len(confs)

    bin_boundaries = np.linspace(0.0, 1.0, num_bins + 1)
    ece = 0.0

    for i in range(num_bins):
        low, high = bin_boundaries[i], bin_boundaries[i + 1]
        mask = (confs >= low) & (confs <= high) if i == num_bins - 1 else (confs >= low) & (confs < high)
        bin_count = np.sum(mask)
        if bin_count > 0:
            bin_acc = np.mean(accs[mask])
            bin_conf = np.mean(confs[mask])
            ece += (bin_count / n) * abs(bin_acc - bin_conf)

    return round(float(ece), 4)

