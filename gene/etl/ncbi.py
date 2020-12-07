"""This module defines ETL methods for the NCBI data source."""
from .base import Base
from gene.database import Database
from gene import PROJECT_ROOT
import logging
from pathlib import Path
import requests

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class NCBI(Base):
    """ETL class for NCBI source"""

    def __init__(self,
                 database: Database,
                 data_url: str = 'https://ftp.ncbi.nlm.nih.gov/gene/DATA/',
                 info_file_url: str = 'https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz',  # noqa: E501
                 grp_file_url: str = 'https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_group.gz'):  # noqa: E501
        """Construct the NCBI ETL instance.

        Args:
            database: gene database for adding new data
            data_url: URL to directory on NCBI website containing source
                material
            info_file_url: URL to gene info file on NCBI website
            grp_file_url: URL to gene group file on NCBI website
        """
        self._database = database
        self._data_url = data_url
        self._info_file_url = info_file_url
        self._grp_file_url = grp_file_url

    def _download_data(self, data_dir):
        requests.get()
        raise NotImplementedError

    def _files_downloaded(self, data_dir: Path) -> bool:
        """Check whether needed source files exist.

        Args:
            data_dir: source data directory

        Returns:
            true if all needed files exist, false otherwise
        """
        files = data_dir.iterdir()

        info_downloaded: bool = False
        grps_downloaded: bool = False
        for f in files:
            if f.name.startswith('ncbi_info'):
                info_downloaded = True
            elif f.name.startswith('ncbi_groups'):
                grps_downloaded = True
        return info_downloaded and grps_downloaded

    def _extract_data(self):
        ncbi_data_dir: Path = Path(PROJECT_ROOT / 'data' / 'ncbi')
        ncbi_files = ncbi_data_dir.iterdir()
        if not self._files_downloaded(ncbi_data_dir):
            self._download_data(ncbi_data_dir)
        versions = [f.name.split('_')[-1]
                    for f in ncbi_files
                    if f.name.startswith('ncbi')]
        self._version = versions.sort()[0]

    def _transform_data(self, *args, **kwargs):
        pass

    def _add_meta(self, *args, **kwargs):
        pass
