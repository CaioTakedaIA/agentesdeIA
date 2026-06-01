from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


EXPECTED_COLUMNS: list[str] = ["id", "name", "category", "value", "date", "status"]

EXPECTED_SCHEMA: dict[str, str] = {
    "id": "int64",
    "name": "object",
    "category": "object",
    "value": "float64",
    "date": "object",
    "status": "object",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    groq_api_key: str = Field(..., alias="GROQ_API_KEY")
    groq_model: str = Field("llama-3.1-8b-instant", alias="GROQ_MODEL")
    data_dir: str = Field("data", alias="DATA_DIR")
    max_context_rows: int = Field(10, alias="MAX_CONTEXT_ROWS")


settings = Settings()
