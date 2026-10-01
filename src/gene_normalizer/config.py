"""Read and provide runtime configuration."""

import logging
from functools import cache
from logging.handlers import RotatingFileHandler

from pydantic_settings import BaseSettings, SettingsConfigDict

from gene_normalizer.schemas import ServiceEnvironment


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


def initialize_logs(log_level: int = logging.INFO) -> None:
    """Configure logging.

    :param log_level: app log level to set
    """
    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(log_level)
    formatter = logging.Formatter(
        "[%(asctime)s] - %(name)s - %(levelname)s : %(message)s"
    )
    fh = RotatingFileHandler(f"{__package__}.log", maxBytes=5_000_000, backupCount=3)
    fh.setFormatter(formatter)
    root.addHandler(fh)
