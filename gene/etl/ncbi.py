"""This module defines ETL methods for the NCBI data source."""
from .base import Base
from gene.database import Database
from gene.schemas import Meta, Gene, SourceName
from gene import PROJECT_ROOT
import logging
from pathlib import Path
import csv
import requests

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class NCBI(Base):
    """ETL class for NCBI source"""

    def __init__(self,
                 database: Database,
                 data_url: str = 'https://ftp.ncbi.nlm.nih.gov/gene/DATA/',
                 info_file_url: str = 'https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz',  # noqa: E501
                 grp_file_url: str = 'https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_group.gz'):  # noqa: E501
        """Construct the NCBI ETL instance.

        :param Database database: gene database for adding new data
        :param str data_url: URL to directory on NCBI website containing gene
            source material
        :param str info_file_url: URL to gene info file on NCBI website
        :param str grp_file_url: URL to gene group file on NCBI website
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

        :param Path data_dir: source data directory
        :return: true if all needed files exist, false otherwise
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
        """Gather data from local files or download from source.
        - Data is expected to be in <PROJECT ROOT>/data/ncbi.
        - For now, data files should all be from the same source data version.
        """
        local_data_dir = PROJECT_ROOT / 'data' / 'ncbi'
        if not self._files_downloaded(local_data_dir):
            self._download_data(local_data_dir)
        local_files = [f for f in local_data_dir.iterdir()
                       if f.startswith('ncbi')]
        local_files.sort(key=lambda f: f.name.split('_')[-1], reverse=True)
        self._info_src = [f for f in local_files
                          if f.name.startswith('ncbi_info')][0]
        self._grps_src = [f for f in local_files
                          if f.name.startswith('ncbi_groups')][0]
        self._version = self._info_src.name.split('_')[-1]

    def _transform_data(self, *args, **kwargs):
        """Modify data and pass to loading functions."""
        self._add_meta()
        # open files, skip headers
        info_file = open(self._info_src.name)
        info = csv.reader(info_file, delimiter='\t')
        next(info)

        with self.database.therapies.batch_writer() as batch:
            for row in info:
                params = {
                    'label': row[2],
                    'concept_id': f"ncbigene:{row[1]}",
                }
                if row[4] != '-':
                    params['aliases'] = row[4].split('|')
                else:
                    params['aliases'] = []
                if row[5] != '-':
                    params['other_identifiers'] = row[5].split('|')
                else:
                    params['other_identifiers'] = []
                if row[10] != '-' and row[12] == 0:
                    params['approved_symbol'] == row[10]
                self._load_data(Gene(**params), batch)
        info_file.close()

        # grps_file = open(self._grps_src.name)
        # grps = csv.reader(grps_file, delimiter='\t')
        # next(grps)
        # grp_file.close()

    def _load_data(self, gene: Gene, batch):
        """Load individual Gene item.

        :param Gene gene: gene instance to load into db
        :param batch: boto3 batch writer
        """
        item = gene.dict()
        concept_id_lower = item['concept_id'].lower()

        if 'aliases' in item:
            item['aliases'] = list(set(item['aliases']))
            aliases = {alias.lower() for alias in item['aliases']}
            for alias in aliases:
                pk = f"{alias}##alias"
                batch.put_item(Item={
                    'label_and_type': pk,
                    'concept_id': concept_id_lower,
                    'src_name': SourceName.NCBI.value
                })

        if item['label']:
            pk = f"{item['label'].lower()}##label"
            batch.put_item(Item={
                'label_and_type': pk,
                'concept_id': concept_id_lower,
                'src_name': SourceName.NCBI.value
            })
        else:
            del item['label']

        item['label_and_type'] = f"{concept_id_lower}##identity"
        item['src_name'] = SourceName.NCBI.value
        batch.put_item(Item=item)

        pass

    def _add_meta(self, *args, **kwargs):
        """Load metadata"""
        metadata = Meta(data_license="TBD",
                        data_license_url="",
                        version=self._version,
                        data_url=self._data_url)
        self.database.metadata.put_item(Item={
            'src_name': SourceName.NCBI.value,
            'data_license': metadata.data_license,
            'data_license_url': metadata.data_license_url,
            'version': metadata.version,
            'data_url': metadata.data_url
        })
