"""This module contains data models for representing VICC normalized
gene records.
"""
from typing import Type, List, Optional, Dict, Union, Any
from pydantic import BaseModel, StrictInt, StrictBool, validator, \
    root_validator
from enum import Enum, IntEnum
from pydantic.fields import Field
from datetime import datetime
from pydantic.types import StrictStr
import re


class SymbolStatus(str, Enum):
    """Define string constraints for symbol status attribute."""

    WITHDRAWN = "withdrawn"
    APPROVED = "approved"
    DISCONTINUED = "discontinued"


class Strand(str, Enum):
    """Define string constraints for strand attribute."""

    FORWARD = "+"
    REVERSE = "-"


class CytobandInterval(BaseModel):
    """GA4GH cytoband interval definition."""

    end: StrictStr
    start: StrictStr
    type = "CytobandInterval"

    @validator('start', 'end')
    def valid_loc(cls, v):
        """Validate start, end"""
        assert bool(re.match(r"^cen|[pq](ter|([1-9][0-9]*(\.[1-9][0-9]*)?))$",
                             v)), r'start/end positions must match the ' \
                                  r'regular expression ^cen|[pq](ter|([1-9]' \
                                  r'[0-9]*(\.[1-9][0-9]*)?))$'
        return v

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['CytobandInterval']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for p in schema.get('properties', {}).values():
                p.pop('title', None)
            schema['example'] = {
                "end": "q22.2",
                "start": "q22.3",
                "type": "CytobandInterval"
            }


class SimpleInterval(BaseModel):
    """GA4GH simple interval definition."""

    end: StrictInt
    start: StrictInt
    type = "SimpleInterval"

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['SimpleInterval']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for p in schema.get('properties', {}).values():
                p.pop('title', None)
            schema['example'] = {
                "end": 44908822,
                "start": 44908821,
                "type": "SimpleInterval"
            }


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


class Location(BaseModel):
    """Define string constraints for the location attribute."""

    id: Optional[StrictStr] = Field(alias='_id')
    type: LocationType


class ChromosomeLocation(Location):
    """GA4GH Chromosome Location definition."""

    species_id: StrictStr
    chr: str
    interval: CytobandInterval

    @validator('species_id')
    def is_curie(cls, v):
        """Validate species_id"""
        assert v.count(':') == 1 and v.find(' ') == -1, 'species_id must be a CURIE'  # noqa: E501
        return v

    @validator('chr')
    def valid_chr(cls, v):
        """Validate chr"""
        assert v.isalnum(), 'chr must have only alphanumeric characters'
        return v

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['ChromosomeLocation']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for p in schema.get('properties', {}).values():
                p.pop('title', None)
            schema['example'] = {
                "chr": "11",
                "interval": {
                    "end": "q22.2",
                    "start": "q22.3",
                    "type": "CytobandInterval"
                },
                "species_id": "taxonomy:9606",
                "type": "ChromosomeLocation"
            }


class SequenceLocation(Location):
    """GA4GH Sequence Location definition."""

    sequence_id: StrictStr
    interval: SimpleInterval

    @validator('sequence_id')
    def is_curie(cls, v):
        """Validate sequence_id"""
        assert v.count(':') == 1 and v.find(' ') == -1, 'sequence_id must be a CURIE'  # noqa: E501
        return v

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['SequenceLocation']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for p in schema.get('properties', {}).values():
                p.pop('title', None)
            schema['example'] = {
                "interval": {
                    "end": 44908822,
                    "start": 44908821,
                    "type": "SimpleInterval"
                },
                "sequence_id": "ga4gh:SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl",
                "type": "SequenceLocation"
            }


class Gene(BaseModel):
    """Gene"""

    concept_id: StrictStr
    symbol: StrictStr
    symbol_status: Optional[SymbolStatus]
    label: Optional[StrictStr]
    strand: Optional[Strand]
    location_annotations: Optional[List[StrictStr]] = []
    locations: Optional[List[Union[SequenceLocation, ChromosomeLocation]]] = []
    aliases: Optional[List[StrictStr]] = []
    previous_symbols: Optional[List[StrictStr]] = []
    xrefs: Optional[List[str]] = []
    associated_with: Optional[List[StrictStr]] = []

    class Config:
        """Configure model example"""

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
                "xrefs": [],
                "symbol_status": None,
                "strand": "-",
                "location": []
            }


class Extension(BaseModel):
    """Define model for VRSATILE Extension."""

    type = "Extension"
    name: StrictStr
    value: Union[StrictStr, List[Dict], List[StrictStr]]

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['Extension']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for p in schema.get('properties', {}).values():
                p.pop('title', None)
            schema['example'] = {
                "type": "Extension",
                "name": "strand",
                "value": "-"
            }


class GeneValueObject(BaseModel):
    """Define model for VRS Gene Value Object."""

    id: StrictStr
    type = "Gene"

    @validator('id')
    def is_curie(cls, v):
        """Validate that `id` is a CURIE"""
        assert v.count(':') == 1 and v.find(' ') == -1, 'id must be a CURIE'
        return v

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['Gene']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for p in schema.get('properties', {}).values():
                p.pop('title', None)
            schema['example'] = {
                "type": "Gene",
                "id": "hgnc:5"
            }


class GeneDescriptor(BaseModel):
    """Define model for VRSATILE Gene Descriptor."""

    id: StrictStr
    type = "GeneDescriptor"
    value: Optional[GeneValueObject]
    value_id: Optional[StrictStr]
    label: Optional[StrictStr]
    xrefs: Optional[List[StrictStr]]
    alternate_labels: Optional[List[StrictStr]]
    extensions: Optional[List[Extension]]

    @validator('value_id', 'id')
    def is_curie(cls, v, field):
        """Validate that `id` and `value_id`, if populated, are CURIES."""
        msg = f'{field.name} must be a CURIE'
        if v is not None:
            assert v.count(':') == 1 and v.find(' ') == -1, msg
        return v

    @root_validator(pre=True)
    def check_value_or_value_id_present(cls, values):
        """Check that at least one of {`value`, `value_id`} is provided."""
        msg = 'Must give values for either `value`, `value_id`, or both'
        value, value_id = values.get('value'), values.get('value_id')
        assert value or value_id, msg
        return values

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['Extension']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for p in schema.get('properties', {}).values():
                p.pop('title', None)
            schema['example'] = {
                "id": "normalize.gene:BRAF",
                "name": "GeneDescriptor",
                "value": {
                    "id": "hgnc:1097",
                    "type": "Gene"
                },
                "label": "BRAF",
                "xrefs": [
                    "ncbigene:673",
                    "ensembl:ENSG00000157764"
                ],
                "alternate_labels": [
                    "B-Raf proto-oncogene, serine/threonine kinase",
                    "BRAF1"
                ],
                "extensions": [
                    {
                        "name": "symbol_status",
                        "value": "approved",
                        "type": "Extension"
                    },
                    {
                        "name": "associated_with",
                        "value": [
                            "vega:OTTHUMG00000157457",
                            "ucsc:uc003vwc.5",
                            "ccds:CCDS5863",
                            "ccds:CCDS87555",
                            "uniprot:P15056",
                            "pubmed:2284096",
                            "pubmed:1565476",
                            "cosmic:BRAF",
                            "omim:164757",
                            "orphanet:119066",
                            "iuphar:1943",
                            "ena.embl:M95712",
                            "refseq:NM_004333"
                        ],
                        "type": "Extension"
                    },
                    {
                        "name": "chromosome_location",
                        "value": {
                            "_id": "ga4gh:VCL.O6yCQ1cnThOrTfK9YUgMlTfM6HTqbrKw",  # noqa: E501
                            "type": "ChromosomeLocation",
                            "species_id": "taxonomy:9606",
                            "chr": "7",
                            "interval": {
                                "end": "q34",
                                "start": "q34",
                                "type": "CytobandInterval"
                            }
                        },
                        "type": "Extension"
                    }
                ]
            }


class GeneGroup(Gene):
    """A grouping of genes based on common attributes."""

    description: StrictStr
    type_identifier: StrictStr
    genes: List[Gene]


class MatchType(IntEnum):
    """Define string constraints for use in Match Type attributes."""

    CONCEPT_ID = 100
    SYMBOL = 100
    PREV_SYMBOL = 80
    ALIAS = 60
    XREF = 60
    ASSOCIATED_WITH = 60
    FUZZY_MATCH = 20
    NO_MATCH = 0


class SourceName(Enum):
    """Define string constraints to ensure consistent capitalization."""

    HGNC = "HGNC"
    ENSEMBL = "Ensembl"
    NCBI = "NCBI"


class SourcePriority(IntEnum):
    """Define priorities for sources when building merged concepts."""

    HGNC = 1
    ENSEMBL = 2
    NCBI = 3


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


class DataLicenseAttributes(BaseModel):
    """Define constraints for data license attributes."""

    non_commercial: StrictBool
    share_alike: StrictBool
    attribution: StrictBool


class ItemTypes(str, Enum):
    """Item types used in DynamoDB."""

    # Must be in descending MatchType order.
    SYMBOL = 'symbol'
    PREVIOUS_SYMBOLS = 'prev_symbol'
    ALIASES = 'alias'
    XREFS = 'xref'
    ASSOCIATED_WITH = 'associated_with'


class SourceMeta(BaseModel):
    """Metadata for a given source to return in response object."""

    data_license: StrictStr
    data_license_url: StrictStr
    version: StrictStr
    data_url: Optional[StrictStr]
    rdp_url: Optional[StrictStr]
    data_license_attributes: Dict[StrictStr, StrictBool]
    genome_assemblies: Optional[List[StrictStr]]

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['SourceMeta']) -> None:
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
                'data_license_attributes': {
                    "non_commercial": False,
                    "share_alike": False,
                    "attribution": False
                },
                "genome_assemblies": None
            }


class MatchesKeyed(BaseModel):
    """Container for matching information from an individual source.
    Used when matches are requested as an object, not an array.
    """

    match_type: MatchType
    records: List[Gene]
    source_meta_: SourceMeta

    class Config:
        """Configure model example"""

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
                    "source_meta_": {
                        "data_license": "custom",
                        "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",  # noqa: E501
                        "version": "20201215",
                        "data_url": "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/",
                        "rdp_url": "https://reusabledata.org/ncbi-gene.html",
                        "data_license_attributes": {
                            "non_commercial": False,
                            "share_alike": False,
                            "attribution": False
                        },
                        "genome_assemblies": None
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
    source_meta_: SourceMeta

    class Config:
        """Configure model example"""

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
                "source_meta_": {
                    "data_license": "custom",
                    "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",  # noqa: E501
                    "version": "20201215",
                    "data_url": "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/",
                    "rdp_url": "https://reusabledata.org/ncbi-gene.html",
                    "data_license_attributes": {
                        "non_commercial": False,
                        "share_alike": False,
                        "attribution": False
                    },
                    "genome_assemblies": None
                }
            }


class ServiceMeta(BaseModel):
    """Metadata regarding the gene-normalization service."""

    name = 'gene-normalizer'
    version: StrictStr
    response_datetime: datetime
    url = 'https://github.com/cancervariants/gene-normalization'

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['ServiceMeta']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for prop in schema.get('properties', {}).values():
                prop.pop('title', None)
            schema['example'] = {
                'name': 'gene-normalizer',
                'version': '0.1.0',
                'response_datetime': '2021-04-05T16:44:15.367831',
                'url': 'https://github.com/cancervariants/gene-normalization'
            }


class SearchService(BaseModel):
    """Define model for returning highest match typed concepts from sources."""

    query: StrictStr
    warnings: Optional[List[Dict]]
    source_matches: Union[Dict[SourceName, MatchesKeyed], List[MatchesListed]]
    service_meta_: ServiceMeta

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['SearchService']) -> None:
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
                                "xrefs": [],
                                "symbol_status": None,
                                "strand": "-",
                                "locations": []
                            }
                        ],
                        "source_meta_": {
                            "data_license": "custom",
                            "data_license_url": "https://uswest.ensembl.org/info/about/legal/index.html",  # noqa: E501
                            "version": "102",
                            "data_url": "http://ftp.ensembl.org/pub/",
                            "rdp_url": None,
                            "data_license_attributes": {
                                "non_commercial": False,
                                "share_alike": False,
                                "attribution": False
                            },
                            "genome_assemblies": "GRCh38"
                        }
                    }
                ],
                "service_meta_": {
                    'name': 'gene-normalizer',
                    'version': '0.1.0',
                    'response_datetime': '2021-04-05T16:44:15.367831',
                    'url': 'https://github.com/cancervariants/gene-normalization'  # noqa: E501
                }
            }


class NormalizeService(BaseModel):
    """Define model for returning normalized concept."""

    query: StrictStr
    warnings: Optional[List[Dict]]
    match_type: MatchType
    gene_descriptor: Optional[GeneDescriptor]
    source_meta_: Optional[Dict[SourceName, SourceMeta]]
    service_meta_: ServiceMeta

    class Config:
        """Configure model example"""

        @staticmethod
        def schema_extra(schema: Dict[str, Any],
                         model: Type['NormalizeService']) -> None:
            """Configure OpenAPI schema"""
            if 'title' in schema.keys():
                schema.pop('title', None)
            for prop in schema.get('properties', {}).values():
                prop.pop('title', None)
            schema['example'] = {
                "query": "BRAF",
                "warnings": [],
                "match_type": 100,
                "gene_descriptor": {
                    "id": "normalize.gene:BRAF",
                    "name": "GeneDescriptor",
                    "value": {
                        "id": "hgnc:1097",
                        "type": "Gene"
                    },
                    "label": "BRAF",
                    "xrefs": [
                        "ncbigene:673",
                        "ensembl:ENSG00000157764"
                    ],
                    "alternate_labels": [
                        "BRAF1"
                    ],
                    "extensions": [
                        {
                            "name": "approved_name",
                            "value": "B-Raf proto-oncogene, serine/threonine kinase",  # noqa: E501
                            "type": "Extension"
                        },
                        {
                            "name": "symbol_status",
                            "value": "approved",
                            "type": "Extension"
                        },
                        {
                            "name": "associated_with",
                            "value": [
                                "vega:OTTHUMG00000157457",
                                "ucsc:uc003vwc.5",
                                "ccds:CCDS5863",
                                "ccds:CCDS87555",
                                "uniprot:P15056",
                                "pubmed:2284096",
                                "pubmed:1565476",
                                "cosmic:BRAF",
                                "omim:164757",
                                "orphanet:119066",
                                "iuphar:1943",
                                "ena.embl:M95712",
                                "refseq:NM_004333"
                            ],
                            "type": "Extension"
                        },
                        {
                            "name": "chromosome_location",
                            "value": {
                                "_id": "ga4gh:VCL.O6yCQ1cnThOrTfK9YUgMlTfM6HTqbrKw",  # noqa: E501
                                "type": "ChromosomeLocation",
                                "species_id": "taxonomy:9606",
                                "chr": "7",
                                "interval": {
                                    "end": "q34",
                                    "start": "q34",
                                    "type": "CytobandInterval"
                                }
                            },
                            "type": "Extension"
                        }
                    ]
                },
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
                                "xrefs": [],
                                "symbol_status": None,
                                "strand": "-",
                                "locations": []
                            }
                        ],
                        "source_meta_": {
                            "data_license": "custom",
                            "data_license_url": "https://uswest.ensembl.org/info/about/legal/index.html",  # noqa: E501
                            "version": "102",
                            "data_url": "http://ftp.ensembl.org/pub/",
                            "rdp_url": None,
                            "data_license_attributes": {
                                "non_commercial": False,
                                "share_alike": False,
                                "attribution": False
                            },
                            "genome_assemblies": "GRCh38"
                        }
                    }
                ],
                "service_meta_": {
                    'name': 'gene-normalizer',
                    'version': '0.1.0',
                    'response_datetime': '2021-04-05T16:44:15.367831',
                    'url': 'https://github.com/cancervariants/gene-normalization'  # noqa: E501
                }
            }
