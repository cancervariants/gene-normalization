"""A base class for extraction, transformation, and loading of data."""
from abc import ABC, abstractmethod
from gene.database import Database
from gene.schemas import SourceName, NamespacePrefix

NORMALIZER_SRCS = {src for src in SourceName.__members__}
NORMALIZER_SRC_PREFIXES = \
    {NamespacePrefix[src.upper()].value for src in NORMALIZER_SRCS}


class Base(ABC):
    """The ETL base class."""

    def __init__(self, database: Database, *args, **kwargs):
        """Extract from sources."""
        self.database = database
        self._load_data(*args, **kwargs)

    @abstractmethod
    def _extract_data(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _transform_data(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _add_meta(self, *args, **kwargs):
        raise NotImplementedError
