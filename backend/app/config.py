import json
from pathlib import Path
from typing import Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "NLP Resume Parser API"
    APP_ENV: str = "development"
    UPLOAD_DIR: Path = Path(__file__).resolve().parent.parent / "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set[str] = {"pdf", "docx", "doc", "jpg", "jpeg", "png"}
    MAX_PDF_PAGES: int = 10
    CORS_ORIGINS: Union[list[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    API_KEY: str | None = None
    RATE_LIMIT_PER_MINUTE: int = 60
    DATABASE_URL: str = "sqlite:///./resumes.db"
    SPACY_MODEL: str = "en_core_web_sm"
    MODEL_DIR: Path | None = None
    USE_ML: bool = True
    USE_SEMANTIC: bool = True

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> list[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()


