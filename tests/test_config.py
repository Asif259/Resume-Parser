import os
import pytest
from app.config import Settings
from app.ml.config import MODEL_DIR

def test_settings_default_values():
    s = Settings()
    assert s.PROJECT_NAME == "NLP Resume Parser API"
    assert "http://localhost:3000" in s.CORS_ORIGINS
    assert s.MAX_FILE_SIZE == 10 * 1024 * 1024
    assert s.USE_ML is True
    assert s.USE_SEMANTIC is True

def test_settings_cors_origins_parsing(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", '["https://app.example.com", "https://api.example.com"]')
    s = Settings()
    assert s.CORS_ORIGINS == ["https://app.example.com", "https://api.example.com"]

    monkeypatch.setenv("CORS_ORIGINS", "https://app.domain.com, https://preview.domain.com")
    s2 = Settings()
    assert s2.CORS_ORIGINS == ["https://app.domain.com", "https://preview.domain.com"]

def test_model_dir_env_override(monkeypatch):
    custom_path = "/tmp/test_models/ner"
    monkeypatch.setenv("MODEL_DIR", custom_path)
    # Re-import or re-evaluate
    import importlib
    import app.ml.config
    importlib.reload(app.ml.config)
    assert str(app.ml.config.MODEL_DIR) == custom_path
