"""This module contains data models for representing VICC normalized
gene records.
"""
from typing import Literal, List, Optional, Dict, Union, Any
from enum import Enum, IntEnum

from pydantic import (
    constr,
    BaseModel,
    StrictBool,
    field_validator,
    StrictStr,
    StrictInt,
    ConfigDict,
)
from ga4gh.vrs import models

from gene.version import __version__


CURIE = constr(pattern=r"^\w[^:]*:.+$")


class Extension(BaseModel):
    """The Extension class provides VODs with a means to extend descriptions with other
    attributes unique to a content provider. These extensions are not expected to be
    natively understood under VRSATILE, but may be used for pre-negotiated exchange of
    message attributes when needed.
    """

    type: Literal["Extension"] = "Extension"
    name: StrictStr
    value: Optional[Any] = None


class GeneValueObject(BaseModel):
    """A reference to a Gene as defined by an authority. For human genes, the use of
    `hgnc <https://registry.identifiers.org/registry/hgnc>` as the gene authority is
    RECOMMENDED.
    """

    id: CURIE
    type: Literal["Gene"] = "Gene"


class GeneDescriptor(BaseModel, extra="forbid"):
    """This descriptor is intended to reference VRS Gene value objects."""

    id: Optional[StrictStr] = None
    type: Literal["GeneDescriptor"] = "GeneDescriptor"
    gene: Union[CURIE, GeneValueObject]
    label: Optional[StrictStr] = None
    description: Optional[StrictStr] = None
    xrefs: List[CURIE] = []
    alternate_labels: List[StrictStr] = []
    extensions: List[Extension] = []

    @field_validator("xrefs")
    def check_count_value(cls, v):
        """Check xrefs value"""
        if v:
            assert len(v) == len(
                {xref for xref in v}
            ), "xrefs must contain unique items"  # noqa: E501
        return v


class SymbolStatus(str, Enum):
    """Define string constraints for symbol status attribute."""

    WITHDRAWN = "withdrawn"
    APPROVED = "approved"
    DISCONTINUED = "discontinued"


class Strand(str, Enum):
    """Define string constraints for strand attribute."""

    FORWARD = "+"
    REVERSE = "-"


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

    MITOCHONDRIA = "MT"


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


class GeneSequenceLocation(BaseModel):
    """Sequence Location model when storing in DynamoDB."""

    type: Literal["SequenceLocation"] = "SequenceLocation"
    start: StrictInt
    end: StrictInt
    sequence_id: constr(pattern=r"^ga4gh:SQ.[0-9A-Za-z_\-]{32}$")  # noqa: F722


# class GeneChromosomeLocation(BaseModel):
#     """Chromosome Location model when storing in DynamDB."""

#     type: Literal["ChromosomeLocation"] = "ChromosomeLocation"
#     species_id: Literal["taxonomy:9606"] = "taxonomy:9606"
#     chr: StrictStr
#     start: StrictStr
#     end: StrictStr


class BaseGene(BaseModel):
    """Base gene model. Provide shared resources for records produced by
    /search and /normalize_unmerged.
    """

    concept_id: CURIE
    symbol: StrictStr
    symbol_status: Optional[SymbolStatus] = None
    label: Optional[StrictStr] = None
    strand: Optional[Strand] = None
    location_annotations: List[StrictStr] = []
    locations: Union[
        List[models.SequenceLocation],
        List[GeneSequenceLocation]
        # List[Union[SequenceLocation, ChromosomeLocation]],
        # List[Union[GeneSequenceLocation, GeneChromosomeLocation]]  # dynamodb
    ] = []
    aliases: List[StrictStr] = []
    previous_symbols: List[StrictStr] = []
    xrefs: List[CURIE] = []
    associated_with: List[CURIE] = []
    gene_type: Optional[StrictStr] = None


class Gene(BaseGene):
    """Gene"""

    match_type: MatchType

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": None,
                "concept_id": "ensembl:ENSG00000157764",
                "symbol": "BRAF",
                "previous_symbols": [],
                "aliases": [],
                "xrefs": [],
                "symbol_status": None,
                "strand": "-",
                "locations": [],
                "location_annotations": [],
                "associated_with": [],
                "gene_type": None,
                "match_type": 100
            }
        }
    )


class GeneGroup(Gene):
    """A grouping of genes based on common attributes."""

    description: StrictStr
    type_identifier: StrictStr
    genes: List[Gene] = []


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


class RecordType(str, Enum):
    """Record item types."""

    IDENTITY = "identity"
    MERGER = "merger"


class RefType(str, Enum):
    """Reference item types."""

    # Must be in descending MatchType order.
    SYMBOL = "symbol"
    PREVIOUS_SYMBOLS = "prev_symbol"
    ALIASES = "alias"
    XREFS = "xref"
    ASSOCIATED_WITH = "associated_with"


class SourceMeta(BaseModel):
    """Metadata for a given source to return in response object."""

    data_license: StrictStr
    data_license_url: StrictStr
    version: StrictStr
    data_url: Optional[StrictStr] = None
    rdp_url: Optional[StrictStr] = None
    data_license_attributes: Dict[StrictStr, StrictBool]
    genome_assemblies: List[StrictStr] = []

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data_license": "custom",
                "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",
                "version": "20201215",
                "data_url": "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/",
                "rdp_url": "https://reusabledata.org/ncbi-gene.html",
                "data_license_attributes": {
                    "non_commercial": False,
                    "share_alike": False,
                    "attribution": False,
                },
                "genome_assemblies": [],
            }
        }
    )


class MatchesKeyed(BaseModel):
    """Container for matching information from an individual source.
    Used when matches are requested as an object, not an array.
    """

    records: List[Gene] = []
    source_meta_: SourceMeta

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
                        "attribution": False,
                    },
                    "genome_assemblies": [],
                },
            }
        }
    )


class MatchesListed(BaseModel):
    """Container for matching information from an individual source.
    Used when matches are requested as an array, not an object.
    """

    source: SourceName
    records: List[Gene] = []
    source_meta_: SourceMeta

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source": "NCBI",
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
                        "attribution": False,
                    },
                    "genome_assemblies": [],
                },
            }
        }
    )


class ServiceMeta(BaseModel):
    """Metadata regarding the gene-normalization service."""

    name: Literal["gene-normalizer"] = "gene-normalizer"
    version: StrictStr
    response_datetime: StrictStr
    url: Literal["https://github.com/cancervariants/gene-normalization"] = "https://github.com/cancervariants/gene-normalization"  # noqa: E501

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "gene-normalizer",
                "version": __version__,
                "response_datetime": "2022-03-23 15:57:14.180908",
                "url": "https://github.com/cancervariants/gene-normalization",
            }
        }
    )


class SearchService(BaseModel):
    """Define model for returning highest match typed concepts from sources."""

    query: StrictStr
    warnings: List[Dict] = []
    source_matches: Union[Dict[SourceName, MatchesKeyed], List[MatchesListed]]
    service_meta_: ServiceMeta

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "BRAF",
                "warnings": [],
                "source_matches": [
                    {
                        "source": "Ensembl",
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
                                "locations": [],
                                "location_annotations": [],
                                "associated_with": [],
                                "gene_type": None,
                                "match_type": 100,
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
                                "attribution": False,
                            },
                            "genome_assemblies": ["GRCh38"],
                        },
                    }
                ],
                "service_meta_": {
                    "name": "gene-normalizer",
                    "version": __version__,
                    "response_datetime": "2022-03-23 15:57:14.180908",
                    "url": "https://github.com/cancervariants/gene-normalization",
                },
            }
        }
    )


class GeneTypeFieldName(str, Enum):
    """Designate source-specific gene type field names for Extensions and
    internal records.
    """

    HGNC = "hgnc_locus_type"
    NCBI = "ncbi_gene_type"
    ENSEMBL = "ensembl_biotype"


class BaseNormalizationService(BaseModel):
    """Base method providing shared attributes to Normalization service classes."""

    query: StrictStr
    warnings: List[Dict] = []
    match_type: MatchType
    service_meta_: ServiceMeta


class NormalizeService(BaseNormalizationService):
    """Define model for returning normalized concept."""

    gene_descriptor: Optional[GeneDescriptor] = None
    source_meta_: Dict[SourceName, SourceMeta] = {}

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "BRAF",
                "warnings": [],
                "match_type": 100,
                "gene_descriptor": {
                    "id": "normalize.gene:BRAF",
                    "type": "GeneDescriptor",
                    "gene": "hgnc:1097",
                    "label": "BRAF",
                    "xrefs": ["ncbigene:673", "ensembl:ENSG00000157764"],
                    "alternate_labels": ["BRAF1", "RAFB1", "B-raf", "NS7", "B-RAF1"],
                    "extensions": [
                        {
                            "name": "approved_name",
                            "value": "B-Raf proto-oncogene, serine/threonine kinase",
                            "type": "Extension",
                        },
                        {
                            "name": "symbol_status",
                            "value": "approved",
                            "type": "Extension",
                        },
                        {
                            "name": "associated_with",
                            "value": [
                                "ccds:CCDS5863",
                                "iuphar:1943",
                                "orphanet:119066",
                                "cosmic:BRAF",
                                "pubmed:2284096",
                                "ucsc:uc003vwc.5",
                                "omim:164757",
                                "refseq:NM_004333",
                                "ccds:CCDS87555",
                                "uniprot:P15056",
                                "ena.embl:M95712",
                                "vega:OTTHUMG00000157457",
                                "pubmed:1565476",
                            ],
                            "type": "Extension",
                        },
                        # {
                        #     "name": "chromosome_location",
                        #     "value": {
                        #         "id": "ga4gh:CL.O6yCQ1cnThOrTfK9YUgMlTfM6HTqbrKw",  # noqa: E501
                        #         "type": "ChromosomeLocation",
                        #         "species_id": "taxonomy:9606",
                        #         "chr": "7",
                        #         "end": "q34",
                        #         "start": "q34",
                        #     },
                        #     "type": "Extension"
                        # }
                    ],
                },
                "source_meta_": {
                    "HGNC": {
                        "data_license": "custom",
                        "data_license_url": "https://www.genenames.org/about/",
                        "version": "20210810",
                        "data_url": "ftp://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/json/hgnc_complete_set.json",  # noqa: E501
                        "rdp_url": None,
                        "data_license_attributes": {
                            "non_commercial": False,
                            "attribution": False,
                            "share_alike": False,
                        },
                        "genome_assemblies": [],
                    },
                    "Ensembl": {
                        "data_license": "custom",
                        "data_license_url": "https://useast.ensembl.org/info/about/legal/disclaimer.html",  # noqa: E501
                        "version": "104",
                        "data_url": "ftp://ftp.ensembl.org/pub/Homo_sapiens.GRCh38.104.gff3.gz",  # noqa: E501
                        "rdp_url": None,
                        "data_license_attributes": {
                            "non_commercial": False,
                            "attribution": False,
                            "share_alike": False,
                        },
                        "genome_assemblies": ["GRCh38"],
                    },
                    "NCBI": {
                        "data_license": "custom",
                        "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",  # noqa: E501
                        "version": "20210813",
                        "data_url": "ftp://ftp.ncbi.nlm.nih.gov",
                        "rdp_url": "https://reusabledata.org/ncbi-gene.html",
                        "data_license_attributes": {
                            "non_commercial": False,
                            "attribution": False,
                            "share_alike": False,
                        },
                        "genome_assemblies": ["GRCh38.p13"],
                    },
                },
                "service_meta_": {
                    "name": "gene-normalizer",
                    "version": __version__,
                    "response_datetime": "2022-03-23 15:57:14.180908",
                    "url": "https://github.com/cancervariants/gene-normalization",
                },
            }
        }
    )


class MatchesNormalized(BaseModel):
    """Matches associated with normalized concept from a single source."""

    records: List[BaseGene] = []
    source_meta_: SourceMeta


class UnmergedNormalizationService(BaseNormalizationService):
    """Response providing source records corresponding to normalization of user query.
    Enables retrieval of normalized concept while retaining sourcing for accompanying
    attributes.
    """

    normalized_concept_id: Optional[CURIE] = None
    source_matches: Dict[SourceName, MatchesNormalized]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "hgnc:108",
                "warnings": [],
                "match_type": 100,
                "service_meta_": {
                    "version": __version__,
                    "response_datetime": "2022-04-26 14:20:54.180240",
                    "name": "gene-normalizer",
                    "url": "https://github.com/cancervariants/gene-normalization",
                },
                "normalized_concept_id": "hgnc:108",
                "source_matches": {
                    "HGNC": {
                        "records": [
                            {
                                "concept_id": "hgnc:108",
                                "symbol": "ACHE",
                                "symbol_status": "approved",
                                "label": "acetylcholinesterase (Cartwright blood group)",  # noqa: E501
                                "strand": None,
                                "location_annotations": [],
                                "locations": [
                                    # {
                                    #     "type": "ChromosomeLocation",
                                    #     "id": "ga4gh:CL.VtdU_0lYXL_o95lXRUfhv-NDJVVpmKoD",  # noqa: E501
                                    #     "species_id": "taxonomy:9606",
                                    #     "chr": "7",
                                    #     "start": "q22.1",
                                    #     "end": "q22.1"
                                    # }
                                ],
                                "aliases": ["3.1.1.7"],
                                "previous_symbols": ["YT"],
                                "xrefs": ["ncbigene:43", "ensembl:ENSG00000087085"],
                                "associated_with": [
                                    "ucsc:uc003uxi.4",
                                    "vega:OTTHUMG00000157033",
                                    "merops:S09.979",
                                    "ccds:CCDS5710",
                                    "omim:100740",
                                    "iuphar:2465",
                                    "ccds:CCDS5709",
                                    "refseq:NM_015831",
                                    "pubmed:1380483",
                                    "uniprot:P22303",
                                    "ccds:CCDS64736",
                                ],
                                "gene_type": "gene with protein product",
                            }
                        ],
                        "source_meta_": {
                            "data_license": "custom",
                            "data_license_url": "https://www.genenames.org/about/",
                            "version": "20220407",
                            "data_url": "ftp://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/json/hgnc_complete_set.json",  # noqa: E501
                            "rdp_url": None,
                            "data_license_attributes": {
                                "non_commercial": False,
                                "share_alike": False,
                                "attribution": False,
                            },
                            "genome_assemblies": [],
                        },
                    },
                    "Ensembl": {
                        "records": [
                            {
                                "concept_id": "ensembl:ENSG00000087085",
                                "symbol": "ACHE",
                                "symbol_status": None,
                                "label": "acetylcholinesterase (Cartwright blood group)",  # noqa: E501
                                "strand": "-",
                                "location_annotations": [],
                                "locations": [
                                    {
                                        "id": "ga4gh:SL.oyhehgtv3XV3iMTlul7XtMQ_5RSAvts6",  # noqa: E501
                                        "type": "SequenceLocation",
                                        "sequenceReference": {
                                            "type": "SequenceReference",
                                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"  # noqa: E501
                                        },
                                        "start": 100889993,
                                        "end": 100896974,
                                    }
                                ],
                                "aliases": [],
                                "previous_symbols": [],
                                "xrefs": ["hgnc:108"],
                                "associated_with": [],
                                "gene_type": "protein_coding",
                            }
                        ],
                        "source_meta_": {
                            "data_license": "custom",
                            "data_license_url": "https://useast.ensembl.org/info/about/legal/disclaimer.html",  # noqa: E501
                            "version": "104",
                            "data_url": "ftp://ftp.ensembl.org/pub/Homo_sapiens.GRCh38.104.gff3.gz",  # noqa: E501
                            "rdp_url": None,
                            "data_license_attributes": {
                                "non_commercial": False,
                                "share_alike": False,
                                "attribution": False,
                            },
                            "genome_assemblies": ["GRCh38"],
                        },
                    },
                    "NCBI": {
                        "records": [
                            {
                                "concept_id": "ncbigene:43",
                                "symbol": "ACHE",
                                "symbol_status": None,
                                "label": "acetylcholinesterase (Cartwright blood group)",  # noqa: E501
                                "strand": "-",
                                "location_annotations": [],
                                "locations": [
                                    {
                                        # "type": "ChromosomeLocation",
                                        # "id": "ga4gh:CL.VtdU_0lYXL_o95lXRUfhv-NDJVVpmKoD",  # noqa: E501
                                        # "species_id": "taxonomy:9606",
                                        # "chr": "7",
                                        # "start": "q22.1",
                                        # "end": "q22.1"
                                    },
                                    {
                                        "id": "ga4gh:SL.OuUQ-JYrkb92VioFp1P9JLGAbVQA1Wqs",  # noqa: E501
                                        "type": "SequenceLocation",
                                        "sequenceReference": {
                                            "type": "SequenceReference",
                                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"  # noqa: E501
                                        },
                                        "start": 100889993,
                                        "end": 100896994,
                                    },
                                ],
                                "aliases": ["YT", "ARACHE", "ACEE", "N-ACHE"],
                                "previous_symbols": ["ACEE"],
                                "xrefs": ["hgnc:108", "ensembl:ENSG00000087085"],
                                "associated_with": ["omim:100740"],
                                "gene_type": "protein-coding",
                            }
                        ],
                        "source_meta_": {
                            "data_license": "custom",
                            "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",  # noqa: E501
                            "version": "20220407",
                            "data_url": "ftp://ftp.ncbi.nlm.nih.gov",
                            "rdp_url": "https://reusabledata.org/ncbi-gene.html",
                            "data_license_attributes": {
                                "non_commercial": False,
                                "share_alike": False,
                                "attribution": False,
                            },
                            "genome_assemblies": ["GRCh38.p13"],
                        },
                    },
                },
            }
        }
    )
