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


class Gene(BaseModel):
    """Gene"""

    label: Optional[str]
    concept_id: str
    symbol: Optional[str]  # might be optional
    previous_symbols: Optional[list]
    aliases: List[str]
    other_identifiers: List[str]
    symbol_status: Optional[SymbolStatus]
    seqid: Optional[str]
    start: Optional[str]
    stop: Optional[str]
    strand: Optional[str]
    location: Optional[str]

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
            # TODO complete example
            # schema['example'] = {
            #     'label': '',
            #     'concept_id': '',
            #     'approved_symbol': '',
            #     'previous_symbols': [],
            #     'aliases': [],
            #     'other_identifiers': [],
            #     'approval_status': Optional[ApprovalStatus]
            # }


class GeneGroup(Gene):
    """A grouping of genes based on common attributes."""

    description: str
    type_identifier: str
    genes: List[Gene]


class MatchType(IntEnum):
    """Define string constraints for use in Match Type attributes."""

    CONCEPT_ID = 100
    APPROVED_SYMBOL = 100
    PREVIOUS_SYMBOL = 80
    ALIAS = 60
    FUZZY_MATCH = 20
    NO_MATCH = 0


class SourceName(Enum):
    """Define string constraints to ensure consistent capitalization."""

    HGNC = "HGNC"
    ENSEMBL = "Ensembl"
    # NCBI = "NCBI"


class SourceIDAfterNamespace(Enum):
    """Define string constraints after namespace."""

    HGNC = ""
    ENSEMBL = "ENSG"
    NCBI = ""


class NamespacePrefix(Enum):
    """Define string constraints for namespace prefixes on concept IDs."""

    HGNC = "hgnc"
    ENSEMBL = "ensembl"
    NCBI = "ncbi"
    ENTREZ = "ncbigene"
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
    HOMEODB = "homeo"
    SNORNABASE = "snornabase"
    ORPHANET = "orphanet"
    PSEUDOGENE = "pseudogene.org"
    HORDE = "horde"
    MEROPS = "merops"
    IMGT = "imgt"
    IUPHAR = "iuphar"
    KZNF_GENE_CATALOG = "knzfgc"
    MAMIT_TRNADB = "mamittrnadb"
    CD = "cd"
    LNCRNADB = "lncrnadb"
    INTERMEDIATE_FILAMENT = "hifdb"


class Meta(BaseModel):
    """Metadata for a given source to return in response object."""

    data_license: str
    data_license_url: str
    version: str
    data_url: Optional[str]
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
            # TODO fill in example meta
            # schema['example'] = {
            #     'data_license': '',
            #     'data_license_url':
            #         '',
            #     'version': '',
            #     'data_url':
            #         'http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/'
            # }


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
            # schema['example'] = {
            #     # TODO fill with example
            #     'normalizer': 'HGNC',
            #     'match_type': 0,
            #     'meta_': {
            #         'data_license': '',
            #         'data_license_url':
            #             '',
            #         'version': '',
            #         'data_url':
            #             'http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/',
            #     },
            # }


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
            # schema['example'] = {
            #     # TODO fill with example
            #     'normalizer': 'HGNC',
            #     'match_type': 0,
            #     'records': [],
            #     'meta_': {
            #         'data_license': '',
            #         'data_license_url':
            #             '',
            #         'version': '',
            #         'data_url':
            #             'http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/',
            #     },
            # }


class Service(BaseModel):
    """Core response schema containing matches for each source"""

    query: str
    warnings: Optional[Dict]
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
            # schema['example'] = {
            #     # TODO add example service
            #     'query': 'BRAF',
            #     'warnings': None,
            #     'meta_': {
            #         'data_license': '',
            #         'data_license_url':
            #             '',
            #         'version': '',
            #         'data_url':
            #             'http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/',
            #     }
            # }
