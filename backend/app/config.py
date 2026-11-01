from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "NLP Resume Parser API"
    UPLOAD_DIR: Path = Path(__file__).resolve().parent.parent / "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set[str] = {"pdf", "docx", "doc", "jpg", "jpeg", "png"}
    DATABASE_URL: str = "sqlite:///./resumes.db"
    SPACY_MODEL: str = "en_core_web_sm"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

