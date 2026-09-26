from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração da API principal, carregada de variáveis de ambiente / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:dataforge@localhost:5432/dataforge"
    insight_url: str = "http://localhost:8001"


settings = Settings()
