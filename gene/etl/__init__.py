"""Module to load and init namespace at package level."""
from .hgnc import HGNC  # noqa: F401
from .ncbi import NCBI  # noqa: F401
from .ensembl import Ensembl  # noqa: F401


class DownloadException(Exception):
    """Exception for failures relating to source file downloads."""

    def __init__(self, *args, **kwargs):
        """Initialize exception."""
        super().__init__(*args, **kwargs)
