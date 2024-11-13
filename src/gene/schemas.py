"""Contains data models for representing VICC normalized gene records."""

from enum import Enum, IntEnum
from typing import Annotated, Literal

from ga4gh.core import domain_models
from ga4gh.vrs import models
from pydantic import (
    BaseModel,
    ConfigDict,
    StrictBool,
    StrictInt,
    StrictStr,
    StringConstraints,
)

from gene import __version__

CURIE_REGEX = r"^\w[^:]*:.+$"


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
    NO_MATCH = 0


class GeneSequenceLocation(BaseModel):
    """Sequence Location model when storing in DynamoDB."""

    type: Literal["SequenceLocation"] = "SequenceLocation"
    start: StrictInt
    end: StrictInt
    sequence_id: Annotated[
        str, StringConstraints(pattern=r"^ga4gh:SQ.[0-9A-Za-z_\-]{32}$")
    ]


class BaseGene(BaseModel):
    """Base gene model. Provide shared resources for records produced by
    /search and /normalize_unmerged.
    """

    concept_id: Annotated[str, StringConstraints(pattern=CURIE_REGEX)]
    symbol: StrictStr
    symbol_status: SymbolStatus | None = None
    label: StrictStr | None = None
    strand: Strand | None = None
    location_annotations: list[StrictStr] = []
    locations: list[models.SequenceLocation] | list[GeneSequenceLocation] = []
    aliases: list[StrictStr] = []
    previous_symbols: list[StrictStr] = []
    xrefs: list[Annotated[str, StringConstraints(pattern=CURIE_REGEX)]] = []
    associated_with: list[Annotated[str, StringConstraints(pattern=CURIE_REGEX)]] = []
    gene_type: StrictStr | None = None


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
                "match_type": 100,
            }
        }
    )


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
    NCBI = ""  # noqa: PIE796


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
    data_url: dict[StrictStr, StrictStr]  # TODO strictness necessary?
    rdp_url: StrictStr | None = None
    data_license_attributes: DataLicenseAttributes
    genome_assemblies: list[StrictStr] = []

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data_license": "custom",
                "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",
                "version": "20201215",
                "data_url": {
                    "info_file": "ftp.ncbi.nlm.nih.govgene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz",
                    "history_file": "ftp.ncbi.nlm.nih.govgene/DATA/gene_history.gz",
                    "assembly_file": "ftp.ncbi.nlm.nih.govgenomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/",
                },
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


class SourceSearchMatches(BaseModel):
    """Container for matching information from an individual source."""

    records: list[Gene] = []
    source_meta_: SourceMeta

    model_config = ConfigDict(json_schema_extra={"example": {}})  # TODO


class ServiceMeta(BaseModel):
    """Metadata regarding the gene-normalization service."""

    name: Literal["gene-normalizer"] = "gene-normalizer"
    version: StrictStr
    response_datetime: StrictStr
    url: Literal["https://github.com/cancervariants/gene-normalization"] = (
        "https://github.com/cancervariants/gene-normalization"
    )

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
    warnings: list[dict] = []
    source_matches: dict[SourceName, SourceSearchMatches]
    service_meta_: ServiceMeta

    model_config = ConfigDict(json_schema_extra={})  # TODO


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
    warnings: list[dict] = []
    match_type: MatchType
    service_meta_: ServiceMeta


class NormalizeService(BaseNormalizationService):
    """Define model for returning normalized concept."""

    normalized_id: str | None = None
    gene: domain_models.Gene | None = None
    source_meta_: dict[SourceName, SourceMeta] = {}

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "BRAF",
                "warnings": [],
                "match_type": 100,
                "normalized_id": "hgnc:1037",
                "gene": {
                    "type": "Gene",
                    "id": "normalize.gene.hgnc:1097",
                    "label": "BRAF",
                    "mappings": [
                        {
                            "coding": {"code": "673", "system": "ncbigene"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "ENSG00000157764", "system": "ensembl"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "CCDS5863", "system": "ccds"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "1943", "system": "iuphar"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "119066", "system": "orphanet"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "BRAF", "system": "cosmic"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "2284096", "system": "pubmed"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "uc003vwc.5", "system": "ucsc"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "164757", "system": "omim"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "NM_004333", "system": "refseq"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "CCDS87555", "system": "ccds"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "P15056", "system": "uniprot"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "M95712", "system": "ena.embl"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "OTTHUMG00000157457", "system": "vega"},
                            "relation": "relatedMatch",
                        },
                        {
                            "coding": {"code": "1565476", "system": "pubmed"},
                            "relation": "relatedMatch",
                        },
                    ],
                    "aliases": ["BRAF1", "RAFB1", "B-raf", "NS7", "B-RAF1"],
                    "extensions": [
                        {
                            "name": "approved_name",
                            "value": "B-Raf proto-oncogene, serine/threonine kinase",
                        },
                        {
                            "name": "symbol_status",
                            "value": "approved",
                        },
                    ],
                },
                "source_meta_": {
                    "HGNC": {
                        "data_license": "custom",
                        "data_license_url": "https://www.genenames.org/about/",
                        "version": "20210810",
                        "data_url": {
                            "complete_set_archive": "ftp://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/json/hgnc_complete_set.json"
                        },
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
                        "data_license_url": "https://useast.ensembl.org/info/about/legal/disclaimer.html",
                        "version": "104",
                        "data_url": {
                            "genome_annotations": "ftp://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.110.gff3.gz"
                        },
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
                        "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",
                        "version": "20210813",
                        "data_url": {
                            "info_file": "ftp.ncbi.nlm.nih.govgene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz",
                            "history_file": "ftp.ncbi.nlm.nih.govgene/DATA/gene_history.gz",
                            "assembly_file": "ftp.ncbi.nlm.nih.govgenomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/",
                        },
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

    records: list[BaseGene] = []
    source_meta_: SourceMeta


class UnmergedNormalizationService(BaseNormalizationService):
    """Response providing source records corresponding to normalization of user query.
    Enables retrieval of normalized concept while retaining sourcing for accompanying
    attributes.
    """

    normalized_concept_id: (
        Annotated[str, StringConstraints(pattern=CURIE_REGEX)] | None
    ) = None
    source_matches: dict[SourceName, MatchesNormalized]

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
                                "label": "acetylcholinesterase (Cartwright blood group)",
                                "strand": None,
                                "location_annotations": [],
                                "locations": [],
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
                            "data_url": {
                                "complete_set_archive": "ftp://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/json/hgnc_complete_set.json"
                            },
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
                                "label": "acetylcholinesterase (Cartwright blood group)",
                                "strand": "-",
                                "location_annotations": [],
                                "locations": [
                                    {
                                        "id": "ga4gh:SL.4taOKYezIxUvFozs6c6OC0bJAQ2zwjxu",
                                        "digest": "4taOKYezIxUvFozs6c6OC0bJAQ2zwjxu",
                                        "type": "SequenceLocation",
                                        "sequenceReference": {
                                            "type": "SequenceReference",
                                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
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
                            "data_license_url": "https://useast.ensembl.org/info/about/legal/disclaimer.html",
                            "version": "104",
                            "data_url": {
                                "genome_annotations": "ftp://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.110.gff3.gz"
                            },
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
                                "label": "acetylcholinesterase (Cartwright blood group)",
                                "strand": "-",
                                "location_annotations": [],
                                "locations": [
                                    {
                                        "id": "ga4gh:SL.OWr9DoyBhr2zpf4uLLcZSvsTSIDElU6R",
                                        "digest": "OWr9DoyBhr2zpf4uLLcZSvsTSIDElU6R",
                                        "type": "SequenceLocation",
                                        "sequenceReference": {
                                            "type": "SequenceReference",
                                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
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
                            "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",
                            "version": "20220407",
                            "data_url": {
                                "info_file": "ftp.ncbi.nlm.nih.govgene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz",
                                "history_file": "ftp.ncbi.nlm.nih.govgene/DATA/gene_history.gz",
                                "assembly_file": "ftp.ncbi.nlm.nih.govgenomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/",
                            },
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
