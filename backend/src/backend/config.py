from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _resolve_path(path: str) -> str:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = (PROJECT_ROOT / resolved).resolve()
    return str(resolved)


def _resolve_sqlite_url(url: str) -> str:
    if not url.startswith("sqlite"):
        return url

    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return url

    db_path = url[len(prefix) :]
    if db_path.startswith("/"):
        return url

    resolved = (PROJECT_ROOT / db_path).resolve()
    return f"sqlite:///{resolved}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'plant_tracking.db'}"
    upload_dir: str = str(PROJECT_ROOT / "data" / "uploads")
    data_dir: str = str(PROJECT_ROOT / "data")
    static_dir: str | None = None
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("database_url", mode="before")
    @classmethod
    def resolve_database_url(cls, value: str) -> str:
        return _resolve_sqlite_url(value)

    @field_validator("upload_dir", "data_dir", mode="before")
    @classmethod
    def resolve_data_paths(cls, value: str) -> str:
        return _resolve_path(value)

    def ensure_dirs(self) -> None:
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()
