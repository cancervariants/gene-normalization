"""The VICC library for normalizing genes."""
from .version import __version__  # noqa: F401
from pathlib import Path
import logging
from os import environ

APP_ROOT = Path(__file__).resolve().parents[0]

if "GENE_NORM_EB_PROD" in environ:
    LOG_FN = "/tmp/gene.log"
else:
    LOG_FN = "gene.log"

logging.basicConfig(
    filename=LOG_FN,
    format="[%(asctime)s] - %(name)s - %(levelname)s : %(message)s")
logger = logging.getLogger("gene")
logger.setLevel(logging.DEBUG)
logger.handlers = []

logging.getLogger("boto3").setLevel(logging.INFO)
logging.getLogger("botocore").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("python_jsonschema_objects").setLevel(logging.INFO)
logging.getLogger("biocommons.seqrepo.seqaliasdb.seqaliasdb").setLevel(logging.INFO)
logging.getLogger("biocommons.seqrepo.fastadir.fastadir").setLevel(logging.INFO)

if "GENE_NORM_EB_PROD" in environ:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)


SEQREPO_DATA_PATH = environ.get("SEQREPO_DATA_PATH",
                                "/usr/local/share/seqrepo/latest")


class DownloadException(Exception):
    """Exception for failures relating to source file downloads."""

    def __init__(self, *args, **kwargs):
        """Initialize exception."""
        super().__init__(*args, **kwargs)


from gene.schemas import SourceName, NamespacePrefix, SourceIDAfterNamespace, ItemTypes  # noqa: E402, E501
ITEM_TYPES = {k.lower(): v.value for k, v in ItemTypes.__members__.items()}

# Sources we import directly (HGNC, Ensembl, NCBI)
SOURCES = {source.value.lower(): source.value
           for source in SourceName.__members__.values()}

# Set of sources we import directly
XREF_SOURCES = {src.lower() for src in SourceName.__members__}

# use to fetch source name from schema based on concept id namespace
# e.g. {"hgnc": "HGNC"}
PREFIX_LOOKUP = {v.value: SourceName[k].value
                 for k, v in NamespacePrefix.__members__.items()
                 if k in SourceName.__members__.keys()}

# use to generate namespace prefix from source ID value
# e.g. {"ensg": "ensembl"}
NAMESPACE_LOOKUP = {v.value.lower(): NamespacePrefix[k].value
                    for k, v in SourceIDAfterNamespace.__members__.items()
                    if v.value != ""}
