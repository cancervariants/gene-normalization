"""This module contains data models for representing VICC normalized
gene records.
"""
from typing import Type, List, Optional, Dict, Union, Any
from pydantic import BaseModel
from enum import Enum, IntEnum


class SymbolStatus(str, Enum):
    """Define string constraints for symbol status attribute."""

    WITHDRAWN = "withdrawn"
    APPROVED = "approved"


class Strand(str, Enum):
    """Define string constraints for strand attribute."""

    FORWARD = "+"
    REVERSE = "-"


class IntervalType(str, Enum):
    """Define string constraints for GA4GH Interval type."""

    CYTOBAND = "CytobandInterval"
    SIMPLE = "SimpleInterval"


class Interval(BaseModel):
    """GA4GH interval definition."""

    end: str
    start: str
    type: IntervalType


class LocationType(str, Enum):
    """Define string constraints for location type attribute."""

    CHROMOSOME = "ChromosomeLocation"
    SEQUENCE = "SequenceLocation"


class Annotation(str, Enum):
    """Define string constraints for annotations when gene location
    is absent.
    """

    NOT_FOUND_ON_REFERENCE = "not on reference assembly"
    UNPLACED = "unplaced"
    RESERVED = "reserved"
    ALT_LOC = "alternate reference locus"


class Chromosome(str, Enum):
    """Define string constraints for chromosomes."""

    MITOCHONDRIA = 'MT'
    # TODO: Un value in NCBI?


class LocationAnnotations(BaseModel):
    """Define string constraints for location annotations."""

    annotation: Optional[Annotation]
    chr: Optional[List[Union[str, Chromosome]]]
    invalid_locations: Optional[List[str]]


class Location(BaseModel):
    """Define string constraints for the location attribute."""

    type: LocationType
    interval: Interval


class ChromosomeLocation(Location):
    """GA4GH Chromosome Location definition."""

    species_id: str
    chr: str


class SequenceLocation(Location):
    """GA4GH Sequence Location definition."""

    sequence_id: str


class Gene(BaseModel):
    """Gene"""

    concept_id: str
    symbol: str
    symbol_status: Optional[SymbolStatus]
    label: Optional[str]
    strand: Optional[Strand]
    location_annotations: Optional[LocationAnnotations]
    locations: Optional[List[Union[ChromosomeLocation, SequenceLocation]]]
    aliases: Optional[List[str]]
    previous_symbols: Optional[List[str]]
    other_identifiers: Optional[List[str]]
    xrefs: Optional[List[str]]

    class Config:
        """Configure model"""

        orm_mode = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['Gene']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for p in schema.get('properties', {}).values():
                p.pop('title', None)
            schema['example'] = {
                "label": None,
                "concept_id": "ensembl:ENSG00000157764",
                "symbol": "BRAF",
                "previous_symbols": [],
                "aliases": [],
                "other_identifiers": [],
                "symbol_status": None,
                "seqid": "7",
                "start": "140719327",
                "stop": "140924929",
                "strand": "-",
                "location": None
            }


class GeneGroup(Gene):
    """A grouping of genes based on common attributes."""

    description: str
    type_identifier: str
    genes: List[Gene]


class MatchType(IntEnum):
    """Define string constraints for use in Match Type attributes."""

    CONCEPT_ID = 100
    SYMBOL = 100
    PREV_SYMBOL = 80
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
    ENSEMBL = "ENSG"
    NCBI = ""


class NamespacePrefix(Enum):
    """Define string constraints for namespace prefixes on concept IDs."""

    HGNC = "hgnc"
    ENSEMBL = "ensembl"
    NCBI = "ncbigene"
    ENTREZ = NCBI
    VEGA = "vega"
    UCSC = "ucsc"
    ENA = "ena.embl"
    REFSEQ = "refseq"
    CCDS = "ccds"
    UNIPROT = "uniprot"
    PUBMED = "pubmed"
    COSMIC = "cosmic"
    OMIM = "omim"
    MIRBASE = "mirbase"
    HOMEODB = "homeodb"
    SNORNABASE = "snornabase"
    ORPHANET = "orphanet"
    PSEUDOGENE = "pseudogene.org"
    HORDE = "hordedb"
    MEROPS = "merops"
    IUPHAR = "iuphar"
    KZNF = "knzfgc"
    MAMIT = "mamittrnadb"
    CD = "hcdmdb"
    LNCRNADB = "lncrnadb"
    IMGT = "imgt"  # .hla? .ligm? leave as is?
    IMGT_GENE_DB = "imgt/gene-db"  # redundant w/ above?
    RFAM = "rfam"


class Meta(BaseModel):
    """Metadata for a given source to return in response object."""

    data_license: str
    data_license_url: str
    version: str
    data_url: Optional[str]
    rdp_url: Optional[str]
    non_commercial: Optional[bool]
    share_alike: Optional[bool]
    attribution: Optional[bool]
    assembly: Optional[str]

    class Config:
        """Enables orm_mode"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['Meta']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for prop in schema.get('properties', {}).values():
                prop.pop('title', None)
            schema['example'] = {
                "data_license": "custom",
                "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",  # noqa: E501
                "version": "20201215",
                "data_url": "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/",
                "rdp_url": "https://reusabledata.org/ncbi-gene.html",
                "non_commercial": False,
                "share_alike": False,
                "attribution": False,
                "assembly": None
            }


class MatchesKeyed(BaseModel):
    """Container for matching information from an individual source.
    Used when matches are requested as an object, not an array.
    """

    match_type: MatchType
    records: List[Gene]
    meta_: Meta

    class Config:
        """Enables orm_mode"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['MatchesKeyed']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for prop in schema.get('properties', {}).values():
                prop.pop('title', None)
            schema['example'] = {
                "NCBI": {
                    "match_type": 0,
                    "records": [],
                    "meta_": {
                        "data_license": "custom",
                        "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",  # noqa: E501
                        "version": "20201215",
                        "data_url": "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/",
                        "rdp_url": "https://reusabledata.org/ncbi-gene.html",
                        "non_commercial": False,
                        "share_alike": False,
                        "attribution": False,
                        "assembly": None
                    }
                }
            }


class MatchesListed(BaseModel):
    """Container for matching information from an individual source.
    Used when matches are requested as an array, not an object.
    """

    source: SourceName
    match_type: MatchType
    records: List[Gene]
    meta_: Meta

    class Config:
        """Enables orm_mode"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['MatchesListed']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for prop in schema.get('properties', {}).values():
                prop.pop('title', None)
            schema['example'] = {
                "source": "NCBI",
                "match_type": 0,
                "records": [],
                "meta_": {
                    "data_license": "custom",
                    "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",  # noqa: E501
                    "version": "20201215",
                    "data_url": "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/",
                    "rdp_url": "https://reusabledata.org/ncbi-gene.html",
                    "non_commercial": False,
                    "share_alike": False,
                    "attribution": False,
                    "assembly": None
                }
            }


class Service(BaseModel):
    """Core response schema containing matches for each source"""

    query: str
    warnings: Optional[List]
    source_matches: Union[Dict[SourceName, MatchesKeyed], List[MatchesListed]]

    class Config:
        """Enables orm_mode"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['Service']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for prop in schema.get('properties', {}).values():
                prop.pop('title', None)
            schema['example'] = {
                "query": "BRAF",
                "warnings": [],
                "source_matches": [
                    {
                        "source": "Ensembl",
                        "match_type": 100,
                        "records": [
                            {
                                "label": None,
                                "concept_id": "ensembl:ENSG00000157764",
                                "symbol": "BRAF",
                                "previous_symbols": [],
                                "aliases": [],
                                "other_identifiers": [],
                                "symbol_status": None,
                                "seqid": "7",
                                "start": "140719327",
                                "stop": "140924929",
                                "strand": "-",
                                "location": None
                            }
                        ],
                        "meta_": {
                            "data_license": "custom",
                            "data_license_url": "https://uswest.ensembl.org/info/about/legal/index.html",  # noqa: E501
                            "version": "102",
                            "data_url": "http://ftp.ensembl.org/pub/",
                            "rdp_url": None,
                            "non_commercial": True,
                            "share_alike": False,
                            "attribution": False,
                            "assembly": "GRCh38"
                        }
                    }
                ]
            }
