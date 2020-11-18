"""This module contains data models for representing VICC normalized
gene records.
"""
from typing import List, Optional, Dict, Union
from pydantic import BaseModel
from enum import Enum, IntEnum


class Gene(BaseModel):
    """Gene"""

    label: str
    concept_id: str
    aliases: List[str]
    other_identifiers: List[str]


class ApprovalStatus(str, Enum):
    """Define string constraints for approval status attribute."""

    WITHDRAWN = "withdrawn"
    APPROVED = "approved"
    INVESTIGATIONAL = "investigational"


class GeneSubclass(BaseModel):  # TODO: Is there a subclass for Gene?
    """Subclass for Gene."""

    approval_status: Optional[ApprovalStatus]
    trade_names: Optional[List[str]]
    label: Optional[str]


class ApprovalStatus(str, Enum):
    """Define string constraints for approval status attribute."""

    WITHDRAWN = "withdrawn"
    APPROVED = "approved"
    INVESTIGATIONAL = "investigational"


class GeneGroup(Gene):
    """A grouping of genes based on common attributes."""

    description: str
    type_identifier: str
    drugs: List[Gene]


class MatchType(IntEnum):
    """Define string constraints for use in Match Type attributes."""

    CONCEPT_ID = 100
    PRIMARY_LABEL = 80
    TRADE_NAME = 80
    ALIAS = 60
    FUZZY_MATCH = 20
    NO_MATCH = 0


class SourceName(Enum):
    """Define string constraints to ensure consistent capitalization."""

    HGNC = "HGNC"
    ENSEMBL = "Ensembl"
    NCBI = "NCBI"


class SourceIDAfterNamespace(Enum):
    """Define string constraints after namespace."""

    HGNC = ""
    ENSEMBL = ""
    NCBI = ""


class NamespacePrefix(Enum):
    """Define string constraints for namespace prefixes on concept IDs."""

    HGNC = "hgnc"
    ENSEMBL = "ensembl"
    NCBI = "ncbigene"  # TODO: Check if just ncbi


class Meta(BaseModel):
    """Metadata for a given source to return in response object."""

    data_license: str
    data_license_url: str
    version: str
    data_url: Optional[str]


class MatchesKeyed(BaseModel):
    """Container for matching information from an individual source.
    Used when matches are requested as an object, not an array.
    """

    match_type: MatchType
    records: List[GeneSubclass]
    meta_: Meta


class MatchesListed(BaseModel):
    """Container for matching information from an individual source.
    Used when matches are requested as an array, not an object.
    """

    source: SourceName
    match_type: MatchType
    records: List[GeneSubclass]
    meta_: Meta


class Service(BaseModel):
    """Core response schema containing matches for each source"""

    query: str
    warnings: Optional[Dict]
    source_matches: Union[Dict[SourceName, MatchesKeyed], List[MatchesListed]]
