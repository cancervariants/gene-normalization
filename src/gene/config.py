"""Read and provide runtime configuration."""

import logging
import os
from typing import Literal

from pydantic import BaseModel

from .schemas import LOCAL_DEV_ENV_NAME, AwsEnvName

_logger = logging.getLogger(__name__)


ENV_VAR_NAME = "GENE_NORM_ENV"


class Config(BaseModel):
    """Define app configuration data object."""

    env: AwsEnvName | Literal[LOCAL_DEV_ENV_NAME]


def _local_dev_config() -> Config:
    """Provide development environment configs

    :return: dev env configs
    """
    return Config(env=LOCAL_DEV_ENV_NAME)


def _dev_config() -> Config:
    """Provide staging env configs

    :return: staging configs
    """
    return Config(env=AwsEnvName.DEVELOPMENT)


def _staging_config() -> Config:
    """Provide staging env configs
    :return: staging configs
    """
    return Config(env=AwsEnvName.STAGING)


def _prod_config() -> Config:
    """Provide production configs
    :return: prod configs
    """
    return Config(env=AwsEnvName.PRODUCTION)


def _default_config() -> Config:
    """Provide default configs. This function sets what they are.
    :return: default configs
    """
    return _local_dev_config()


_CONFIG_MAP = {
    LOCAL_DEV_ENV_NAME: _local_dev_config,
    AwsEnvName.DEVELOPMENT: _dev_config,
    AwsEnvName.STAGING: _staging_config,
    AwsEnvName.PRODUCTION: _prod_config,
}


def _set_config() -> Config:
    """Set configs based on environment variable `GENE_NORM_ENV`.

    :return: complete config object with environment-specific parameters
    """
    raw_env_value = os.environ.get(ENV_VAR_NAME)
    if not raw_env_value:
        return _default_config()
    if raw_env_value == LOCAL_DEV_ENV_NAME:
        return _local_dev_config()
    try:
        env_value = AwsEnvName(raw_env_value)
    except ValueError:
        _logger.error(
            "Unrecognized value for %s: %s. Using default configs",
            ENV_VAR_NAME,
            raw_env_value,
        )
        return _default_config()
    return _CONFIG_MAP[env_value]()


config = _set_config()
