from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database Configuration
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "rag_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/rag_db"

    # API Keys
    openai_api_key: str
    google_api_key: str

    # Basic Authentication
    basic_auth_username: str = "admin"
    basic_auth_password: str = "changeme"

    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    @property
    def async_database_url(self) -> str:
        """Get async database URL for asyncpg."""
        return self.database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")


# Global settings instance
settings = Settings()
