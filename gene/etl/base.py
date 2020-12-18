"""A base class for extraction, transformation, and loading of data."""
from abc import ABC, abstractmethod
from gene.database import Database
from gene.schemas import SourceName, NamespacePrefix


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

    def _get_normalizer_prefixes(self):
        """Retrieve normalizer sources' prefixes.

        :return: A list containing normalizer sources' prefixes
        """
        normalizer_srcs = {src for src in SourceName.__members__}
        normalizer_srcs_prefixes = list()
        for src in normalizer_srcs:
            normalizer_srcs_prefixes.append(NamespacePrefix[src.upper()].value)
        return normalizer_srcs_prefixes
