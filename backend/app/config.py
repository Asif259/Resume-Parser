from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "NLP Resume Parser API"
    UPLOAD_DIR: Path = Path(__file__).resolve().parent.parent / "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set[str] = {"pdf", "docx", "doc", "jpg", "jpeg", "png"}
    MAX_PDF_PAGES: int = 10
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    API_KEY: str | None = None
    RATE_LIMIT_PER_MINUTE: int = 60
    DATABASE_URL: str = "sqlite:///./resumes.db"
    SPACY_MODEL: str = "en_core_web_sm"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

