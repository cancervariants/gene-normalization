"""Define app-wide validation models"""

from enum import StrEnum


class ServiceEnvironment(StrEnum):
    """Define current runtime environment."""

    LOCAL = "local"
    TEST = "test"
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"
