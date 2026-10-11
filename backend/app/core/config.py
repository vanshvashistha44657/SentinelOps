from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SentinelOps"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Database
    DATABASE_URL: str
    DB_OVERRIDE: Optional[str] = None
    RENDER: bool = False
    RENDER_EXTERNAL_HOSTNAME: Optional[str] = None
    RENDER_GIT_COMMIT: Optional[str] = None

    @field_validator("DATABASE_URL", "DB_OVERRIDE", mode="before")
    @classmethod
    def normalize_postgres_url(cls, value):
        # Managed providers can return the historical postgres:// scheme.
        if isinstance(value, str) and value.startswith("postgres://"):
            return "postgresql+psycopg2://" + value[len("postgres://"):]
        return value

    @model_validator(mode="after")
    def require_postgres_on_render(self):
        if self.RENDER and not self.DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://")):
            raise ValueError("Render deployments require a managed PostgreSQL DATABASE_URL")
        return self


    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    TRUSTED_HOSTS: str = "localhost,127.0.0.1"
    SENSOR_STALE_AFTER_SECONDS: int = 180
    NETWORK_CONNECTIVITY_TARGET: str = "1.1.1.1"
    NETWORK_RETENTION_DAYS: int = 90

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.CORS_ORIGINS.split(",") if item.strip()]

    @property
    def trusted_hosts(self) -> list[str]:
        hosts = [item.strip() for item in self.TRUSTED_HOSTS.split(",") if item.strip()]
        if self.RENDER_EXTERNAL_HOSTNAME and self.RENDER_EXTERNAL_HOSTNAME not in hosts:
            hosts.append(self.RENDER_EXTERNAL_HOSTNAME)
        return hosts
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
