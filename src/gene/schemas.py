"""Contains data models for representing VICC normalized gene records."""
from enum import Enum, IntEnum, StrEnum
from typing import Dict, List, Literal, Optional, Union

from ga4gh.core._internal.models import Extension, Gene
from ga4gh.vrs import models
from pydantic import (
    BaseModel,
    ConfigDict,
    StrictBool,
    StrictStr,
    constr,
)

from gene.version import __version__

###############################################################################
# namespace/identification
###############################################################################

CURIE = constr(pattern=r"^\w[^:]*:.+$")


class SourceName(Enum):
    """Define string constraints to ensure consistent capitalization."""

    HGNC = "HGNC"
    ENSEMBL = "Ensembl"
    NCBI = "NCBI"


# lowercase imported source name to correctly-cased name, e.g. {"ensembl": "Ensembl"}
SOURCES = {
    source.value.lower(): source.value for source in SourceName.__members__.values()
}


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


# use to fetch source name from schema based on concept id namespace
# e.g. {"hgnc": "HGNC"}
PREFIX_LOOKUP = {
    v.value: SourceName[k].value
    for k, v in NamespacePrefix.__members__.items()
    if k in SourceName.__members__.keys()
}

# use to generate namespace prefix from source ID value
# e.g. {"ensg": "ensembl"}
NAMESPACE_LOOKUP = {
    v.value.lower(): NamespacePrefix[k].value
    for k, v in SourceIDAfterNamespace.__members__.items()
    if v.value != ""
}

###############################################################################
# gene elements
###############################################################################


class SymbolStatus(str, Enum):
    """Define string constraints for symbol status attribute."""

    WITHDRAWN = "withdrawn"
    APPROVED = "approved"
    DISCONTINUED = "discontinued"


class SymbolStatusExtension(Extension):
    """Define symbol status extension object structure."""

    name: Literal["symbol_status"] = "symbol_status"
    value: SymbolStatus


class Strand(str, Enum):
    """Define string constraints for strand attribute."""

    FORWARD = "+"
    REVERSE = "-"


class StrandExtension(Extension):
    """Define strand extension object structure."""

    name: Literal["strand"] = "strand"
    value: Strand


class ApprovedNameExtension(Extension):
    """Define approved name object structure."""

    name: Literal["approved_name"] = "approved_name"
    value: StrictStr


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


class LocationAnnotationsExtension(Extension):
    """Define location annotation extension object structure.

    # TODO: what even is this?
    """

    name: Literal["location_annotations"] = "location_annotations"
    value: List[Union[Annotation, Chromosome]]


class GeneTypeExtensionName(StrEnum):
    """Designate source-specific gene type field names for Extensions and
    internal records.
    """

    HGNC = "hgnc_locus_type"
    NCBI = "ncbi_gene_type"
    ENSEMBL = "ensembl_biotype"


class GeneTypeExtension(Extension):
    """Define gene type extension object structure."""

    name: GeneTypeExtensionName
    value: StrictStr


class SequenceLocationExtensionName(StrEnum):
    """Define name restrictions for source-provided sequence location extensions."""

    NCBI_LOCATIONS = "ncbi_locations"
    ENSEMBL_LOCATIONS = "ensembl_locations"


class SequenceLocationExtension(Extension):
    """Define structure for sequence location extension."""

    name: SequenceLocationExtensionName
    value: List[models.SequenceLocation]


class PreviousSymbolsExtension(Extension):
    """Define previous symbols extension object structure."""

    name: Literal["previous_symbols"] = "previous_symbols"
    value: List[StrictStr]


# class GeneGroup(Gene):
#     """A grouping of genes based on common attributes."""
#
#     description: StrictStr
#     type_identifier: StrictStr
#     genes: List[Gene] = []

###############################################################################
# database and match components
###############################################################################


class RecordType(str, Enum):
    """Record item types."""

    IDENTITY = "identity"  # TODO i think this should change
    MERGER = "merger"


class RefType(str, Enum):
    """Reference item types."""

    # Must be in descending MatchType order.
    SYMBOL = "symbol"
    PREVIOUS_SYMBOLS = "prev_symbol"
    ALIASES = "alias"
    XREFS = "xref"


# collective name to singular name, e.g. {"previous_symbols": "prev_symbol"}
ITEM_TYPES = {k.lower(): v.value for k, v in RefType.__members__.items()}

###############################################################################
# response components
###############################################################################


class DataLicenseAttributes(BaseModel):
    """Define constraints for data license attributes."""

    non_commercial: StrictBool
    share_alike: StrictBool
    attribution: StrictBool


class SourceMeta(BaseModel):
    """Metadata for a given source to return in response object."""

    data_license: StrictStr
    data_license_url: StrictStr
    version: StrictStr
    data_url: Dict[StrictStr, StrictStr]
    rdp_url: Optional[StrictStr] = None
    data_license_attributes: DataLicenseAttributes
    genome_assemblies: List[StrictStr] = []

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


class ServiceMeta(BaseModel):
    """Metadata regarding the gene-normalization service."""

    name: Literal["gene-normalizer"] = "gene-normalizer"
    version: StrictStr
    response_datetime: StrictStr
    url: Literal[
        "https://github.com/cancervariants/gene-normalization"
    ] = "https://github.com/cancervariants/gene-normalization"

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


class MatchType(IntEnum):
    """Define string constraints for use in Match Type attributes."""

    CONCEPT_ID = 100
    SYMBOL = 100
    PREV_SYMBOL = 80
    ALIAS = 60
    XREF = 60
    FUZZY_MATCH = 20
    NO_MATCH = 0


REF_TO_MATCH_MAP = {
    RefType.SYMBOL: MatchType.SYMBOL,
    RefType.PREVIOUS_SYMBOLS: MatchType.PREV_SYMBOL,
    RefType.ALIASES: MatchType.ALIAS,
    RefType.XREFS: MatchType.XREF,
}


class WarningType(StrEnum):
    """Define possible warning types."""

    STRIPPED_QUERY = "stripped_query"
    MULTIPLE_NORMALIZED_CONCEPTS = "multiple_normalized_concepts_found"
    INFERRED_NAMESPACE = "inferred_namespace"  # TODO implement
    NBSP = "non_breaking_space_characters"


class QueryWarning(BaseModel):
    """Define warning structure."""

    type: WarningType
    description: StrictStr


class _Service(BaseModel):
    """Define base service response object."""

    query: StrictStr
    additional_params: Optional[Dict] = None
    service_meta_: ServiceMeta


class ResultSourceMeta(BaseModel):
    """Structure source metadata for all results objects."""

    hgnc: Optional[SourceMeta] = None
    ensembl: Optional[SourceMeta] = None
    ncbi: Optional[SourceMeta] = None


class _Result(BaseModel):
    """Define base lookup result object. Returned by QueryHandler methods like
    `normalize()`, and included in REST responses.
    """

    warnings: Optional[List[QueryWarning]] = None
    source_meta: ResultSourceMeta


class GeneMatch(BaseModel):
    """Structure individual gene match."""

    match_type: MatchType
    gene: Gene


class SearchResult(_Result):
    """Result object for `search()` endpoint."""

    hgnc_matches: Optional[List[GeneMatch]] = None
    ensembl_matches: Optional[List[GeneMatch]] = None
    ncbi_matches: Optional[List[GeneMatch]] = None


class SearchService(_Service):
    """Define response object for /search endpoint."""

    results: SearchResult


class NormalizeResult(_Result):
    """Result object for `normalize()` method."""

    normalized_id: Optional[CURIE] = None
    match: Optional[GeneMatch] = None


class NormalizeService(_Service):
    """Define response object for /normalize endpoint."""

    result: NormalizeResult


class NormalizeUnmergedMatches(BaseModel):
    """Structure individual source matches under the `unmerged()` method."""

    hgnc_genes: Optional[List[GeneMatch]] = None
    ensembl_genes: Optional[List[GeneMatch]] = None
    ncbi_genes: Optional[List[GeneMatch]] = None

    def get_matches_by_source(self) -> Dict[SourceName, Optional[List[GeneMatch]]]:
        """Get a more easily computable directory of matches by source

        :return: Dictionary mapping SourceName instances to gene match lists
        """
        matches = {}
        for field_name in self.model_fields:
            key = SourceName(SOURCES[field_name.split("_")[0]])
            matches[key] = self.__getattribute__(field_name)
        return matches


class NormalizeUnmergedResult(_Result):
    """Match object for `normalize_unmerged()` method."""

    normalized_id: Optional[CURIE] = None
    source_genes: NormalizeUnmergedMatches


class NormalizeUnmergedService(_Service):
    """Define response object for /normalize_unmerged endpoint."""

    result: NormalizeUnmergedResult
