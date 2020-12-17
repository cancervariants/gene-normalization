"""The VICC library for normalizing genes."""
from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).resolve().parents[1]
logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class DownloadException(Exception):
    """Exception for failures relating to source file downloads."""

    def __init__(self, *args, **kwargs):
        """Initialize exception."""
        super().__init__(*args, **kwargs)
