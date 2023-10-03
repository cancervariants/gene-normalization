"""The VICC library for normalizing genes."""
import logging
from os import environ
from pathlib import Path

from .version import __version__  # noqa: F401

APP_ROOT = Path(__file__).resolve().parent

logging.basicConfig(
    filename="gene.log", format="[%(asctime)s] - %(name)s - %(levelname)s : %(message)s"
)
logger = logging.getLogger("gene")
logger.setLevel(logging.DEBUG)
logger.handlers = []

logging.getLogger("boto3").setLevel(logging.INFO)
logging.getLogger("botocore").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("python_jsonschema_objects").setLevel(logging.INFO)
logging.getLogger("biocommons.seqrepo.seqaliasdb.seqaliasdb").setLevel(logging.INFO)
logging.getLogger("biocommons.seqrepo.fastadir.fastadir").setLevel(logging.INFO)


SEQREPO_ROOT_DIR = Path(
    environ.get("SEQREPO_ROOT_DIR", "/usr/local/share/seqrepo/latest")
)


class DownloadException(Exception):  # noqa: N818
    """Exception for failures relating to source file downloads."""


from gene.schemas import (  # noqa: E402
    NamespacePrefix,
    RefType,
    SourceIDAfterNamespace,
    SourceName,
)

ITEM_TYPES = {k.lower(): v.value for k, v in RefType.__members__.items()}

# Sources we import directly (HGNC, Ensembl, NCBI)
SOURCES = {
    source.value.lower(): source.value for source in SourceName.__members__.values()
}

# Set of sources we import directly
XREF_SOURCES = {src.lower() for src in SourceName.__members__}

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
