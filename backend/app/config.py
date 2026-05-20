from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://api_pulse:api_pulse_password@postgres:5432/api_pulse"
    frontend_origin: str = "http://localhost:5173"
    request_timeout_seconds: float = 20.0
    response_summary_max_chars: int = 2000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
