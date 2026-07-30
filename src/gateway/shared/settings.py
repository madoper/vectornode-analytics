__anchor__ = "settings"
# schema-ref: project-schema.yaml#/shared_modules/1

from pydantic_settings import BaseSettings

APP_VERSION: str = "0.5.0"


class Settings(BaseSettings):
    app_env: str = "development"
    app_debug: bool = True
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "podft"
    postgres_password: str = "podft-secret"
    postgres_db: str = "podft"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "podft-neo4j"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    minio_host: str = "localhost"
    minio_port: int = 9000
    minio_access_key: str = "podft-minio"
    minio_secret_key: str = "podft-minio-secret"
    minio_bucket_raw: str = "raw-documents"
    minio_bucket_parsed: str = "parsed-documents"
    minio_bucket_exports: str = "exports"
    minio_bucket_internal: str = "internal-documents"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_summarization_provider: str = "openrouter"
    llm_summarization_model: str = "google/gemini-2.0-flash-001"

    gigachat_client_id: str = "019ade09-90b2-7d5b-8ebf-aaee57d985df"
    gigachat_secret: str = "cd534c2f-c6d3-4570-b90d-44e1f2418ac6"

    gateway_ro_user: str = "gateway_ro"
    gateway_ro_password: str = "gateway_ro_secret"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
