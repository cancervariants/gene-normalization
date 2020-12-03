"""This module defines the Ensembl ETL methods."""
from .base import Base
from gene import PROJECT_ROOT
from gene.schemas import SourceName, ApprovalStatus, NamespacePrefix  # noqa: F401, E501
import logging
from gene.database import GENES_TABLE, METADATA_TABLE  # noqa: F401
# from BCBio.GFF import GFFExaminer

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class Ensembl(Base):
    """ETL the Ensembl source into the normalized database."""

    def __init__(self,
                 data_url='http://ftp.ensembl.org/pub/',
                 data_file_url='http://ftp.ensembl.org/pub/release-102/gtf/'
                               'homo_sapiens/Homo_sapiens.GRCh38.102.gtf.gz'
                 ):
        """Initialize Ensembl ETL class."""
        self._data_url = data_url
        self._data_file_url = data_file_url
        self._version = '102'
        self._load_data()

    def _download_data(self, *args, **kwargs):
        pass

    def _extract_data(self, *args, **kwargs):
        """Extract data from the Ensembl source."""
        if 'data_path' in kwargs:
            self._data_src = kwargs['data_path']
        else:
            wd_dir = PROJECT_ROOT / 'data' / 'ensembl'
            wd_dir.mkdir(exist_ok=True, parents=True)  # TODO needed?
            try:
                self._data_src = sorted(list(wd_dir.iterdir()))[-1]
            except IndexError:
                raise FileNotFoundError  # TODO Ensembl update function here
        pass

    def _transform_data(self, *args, **kwargs):
        """Transform the Ensembl source."""
        pass

    def _load_data(self, *args, **kwargs):
        """Load the Ensembl source into normalized database."""
        self._download_data()
        self._extract_data()
        self._transform_data()
        self._add_meta()

    def _add_meta(self, *args, **kwargs):
        """Add Ensembl metadata."""
        METADATA_TABLE.put_item(
            Item={
                'src_name': SourceName.ENSEMBL.value,
                'data_license': 'temp',
                'data_license_url': 'temp',
                'version': self._version,
                'data_url': self._data_url
            }
        )
