from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    authentik_issuer: str
    authentik_client_id: str = ""

    {% if cookiecutter.add_arq == "y" %}
    redis_url: str = "redis://localhost:6379"
    {% endif %}

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = ""
    minio_secure: bool = False


settings = Settings()
