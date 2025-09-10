"""Read and provide runtime configuration."""

from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from gene.schemas import ServiceEnvironment


class Settings(BaseSettings):
    """Create app settings

    There's no singleton effect here, so every new call to this class will re-compute
    configuration settings, defaults, etc.
    """

    model_config = SettingsConfigDict(
        env_prefix="gene_norm_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: ServiceEnvironment = ServiceEnvironment.DEV
    debug: bool = False
    test: bool = False
    db_url: str = "http://localhost:8000"


@cache
def get_config() -> Settings:
    """Get runtime configuration.

    This function is cached, so the config object only gets created/calculated once.

    :return: Settings instance
    """
    return Settings()
