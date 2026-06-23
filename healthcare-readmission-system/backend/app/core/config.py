from pathlib import Path
import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Healthcare Readmission API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    debug: bool = False
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    database_url: str | None = None

    project_root: Path = Path(__file__).resolve().parents[3]
    models_dir: Path = project_root / "models"
    dashboard_data_dir: Path = project_root / "dashboard" / "data"
    processed_data_file: Path = project_root / "data" / "processed" / "cleaned_data.csv"
    best_model_path: Path = models_dir / "best_model.joblib"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [item.strip() for item in value.split(",") if item.strip()]
        return value


settings = Settings()
