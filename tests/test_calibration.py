from pathlib import Path
import pytest
from app.ml.calibration import ConfidenceCalibrator, compute_ece
from app.schemas.evidence import FieldEvidence
from app.services.confidence import compute_overall_confidence, flag_low_confidence

def test_calibrator_identity_at_temp_one():
    calibrator = ConfidenceCalibrator(temperature=1.0)
    assert calibrator.calibrate(0.9) == pytest.approx(0.9, abs=0.01)
    assert calibrator.calibrate(0.5) == pytest.approx(0.5, abs=0.01)
    assert calibrator.calibrate(0.1) == pytest.approx(0.1, abs=0.01)

def test_calibrator_temperature_effects():
    # T > 1.0 pulls toward 0.5 (softens overconfident scores)
    softener = ConfidenceCalibrator(temperature=2.0)
    assert softener.calibrate(0.95) < 0.95
    assert softener.calibrate(0.05) > 0.05

    # T < 1.0 pushes away from 0.5 (sharpens)
    sharpener = ConfidenceCalibrator(temperature=0.5)
    assert sharpener.calibrate(0.95) > 0.95

def test_calibrator_fit_and_save(tmp_path: Path):
    # Simulated overconfident model: outputs 0.9 confidence, but only 60% accurate
    confidences = [0.9] * 10 + [0.1] * 10
    labels = [True] * 6 + [False] * 4 + [False] * 9 + [True] * 1

    calibrator = ConfidenceCalibrator()
    learned_t = calibrator.fit(confidences, labels)
    assert learned_t > 1.0  # Learned that model is overconfident

    save_path = tmp_path / "calibration.json"
    calibrator.save(save_path)
    loaded = ConfidenceCalibrator.load(save_path)
    assert loaded.temperature == calibrator.temperature

def test_compute_ece():
    # Perfectly calibrated
    confs = [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.1]
    accs = [True, True, True, True, True, True, True, True, True, False]
    ece = compute_ece(confs, accs, num_bins=5)
    assert ece < 0.15

def test_confidence_service_uses_calibrated_confidence():
    evidence = {
        "field1": FieldEvidence(
            value="Val1",
            source_section="experience",
            source_text="Val1",
            confidence=0.95,
            calibrated_confidence=0.50,
        )
    }
    # flag_low_confidence threshold is 0.6; calibrated 0.50 should trigger flag even though raw is 0.95
    flagged = flag_low_confidence(evidence, threshold=0.6)
    assert "field1" in flagged

    # compute_overall_confidence should use 0.50
    overall = compute_overall_confidence(evidence)
    assert overall == pytest.approx(0.50, abs=0.01)

