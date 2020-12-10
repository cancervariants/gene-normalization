"""This module defines ETL methods for the NCBI data source."""
from .base import Base
from gene import PROJECT_ROOT
from gene.database import Database
from gene.schemas import Meta, Gene, SourceName, NamespacePrefix
import logging
from pathlib import Path
import csv
import requests
from datetime import datetime
import gzip
import shutil

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
        :param str info_file_url: default URL to gene info file on NCBI website
        :param str grp_file_url: default URL to gene group file on NCBI website
        """
        self._database = database
        self._data_url = data_url
        self._info_file_url = info_file_url
        self._grp_file_url = grp_file_url
        self._valid_prefixes = {v.value for v
                                in NamespacePrefix.__members__.values()}
        self._extract_data()
        self._transform_data()

    def _download_data(self, data_dir):
        logger.info('Downloading NCBI Gene...')
        response = requests.get(self._info_file_url, stream=True)
        if response.status_code == 200:
            version = datetime.today().strftime('%Y%m%d')
            with open("/tmp/ncbi_gene_info.gz", 'wb') as f:
                f.write(response.content)
            with gzip.open("/tmp/ncbi_gene_info.gz", "rb") as gz:
                with open(f"{PROJECT_ROOT}/data/ncbi/"
                          f"ncbi_info_{version}.tsv", 'wb') as f_out:
                    shutil.copyfileobj(gz, f_out)

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
                       if f.name.startswith('ncbi')]
        local_files.sort(key=lambda f: f.name.split('_')[-1], reverse=True)
        self._info_src = [f for f in local_files
                          if f.name.startswith('ncbi_info')][0]
        self._grps_src = [f for f in local_files
                          if f.name.startswith('ncbi_groups')][0]
        self._version = self._info_src.name.split('_')[-1]

    def _transform_data(self):
        """Modify data and pass to loading functions."""
        self._add_meta()
        # open files, skip headers
        info_file = open(self._info_src, 'r')
        info = csv.reader(info_file, delimiter='\t')
        next(info)

        with self._database.genes.batch_writer() as batch:
            for row in info:
                params = {
                    'concept_id': f"ncbigene:{row[1]}",
                }
                # get symbol
                if row[2] != '-':
                    params['symbol'] = row[2]
                else:
                    logger.error(f"Couldn't read symbol from row: {row}")
                # get aliases
                if row[4] != '-':
                    params['aliases'] = row[4].split('|')
                else:
                    params['aliases'] = []
                # get other identifiers
                if row[5] != '-':
                    xrefs = row[5].split('|')
                    other_ids = []
                    for ref in xrefs:
                        if ref.startswith("HGNC:"):
                            other_id = NamespacePrefix.HGNC.value + ref[10:]
                            other_ids.append(other_id)
                        elif ref.startswith("MIM:"):
                            other_id = NamespacePrefix.MIM.value + \
                                ref.split(':')[1]
                            other_ids.append(other_id)
                        else:
                            prefix = ref.split(':')[0].lower()
                            if prefix not in self._valid_prefixes:
                                raise Exception(f"invalid ref prefix {prefix}"
                                                f" in:\n {row}")
                            else:
                                other_id = prefix + ref.split(':')[-1]
                                other_ids.append(other_id)
                    params['other_identifiers'] = other_ids
                else:
                    params['other_identifiers'] = []
                # TODO how to handle chromosome/start/stop? maybe map_location?
                # maybe pull from gene2refseq file?
                self._load_data(Gene(**params), batch)
        info_file.close()

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

    def _add_meta(self):
        """Load metadata"""
        metadata = Meta(data_license="TBD",
                        data_license_url="TBD",
                        version=self._version,
                        data_url=self._data_url)
        self._database.metadata.put_item(Item={
            'src_name': SourceName.NCBI.value,
            'data_license': metadata.data_license,
            'data_license_url': metadata.data_license_url,
            'version': metadata.version,
            'data_url': metadata.data_url
        })
