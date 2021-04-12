"""The VICC library for normalizing genes."""
from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).resolve().parents[0]
logging.basicConfig(
    filename='gene.log',
    format='[%(asctime)s] %(levelname)s : %(message)s')
logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


__version__ = "0.1.7"


class DownloadException(Exception):
    """Exception for failures relating to source file downloads."""

    def __init__(self, *args, **kwargs):
        """Initialize exception."""
        super().__init__(*args, **kwargs)
