"""This module defines ETL methods for the NCBI data source."""
from .base import Base
from gene import PROJECT_ROOT, DownloadException
from gene.database import Database
from gene.schemas import Meta, Gene, SourceName, NamespacePrefix
import logging
from pathlib import Path
import csv
import requests
from datetime import datetime
import gzip
import shutil
from os import remove

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)

# set of valid concept ID prefixes for parsing cross-refs to other sources
VALID_CID_PREFIXES = {v.value for v in NamespacePrefix.__members__.values()}


class NCBI(Base):
    """ETL class for NCBI source"""

    def __init__(self,
                 database: Database,
                 data_url: str = 'https://ftp.ncbi.nlm.nih.gov/gene/DATA/',
                 info_file_url: str = 'https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz',  # noqa: E501
                 history_file_url: str = 'https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_history.gz'):  # noqa: E501
        """Construct the NCBI ETL instance.

        :param Database database: gene database for adding new data
        :param str data_url: URL to directory on NCBI website containing gene
            source material
        :param str info_file_url: default URL to gene info file on NCBI website
        :param str history_file_url: default URL to gene group file on NCBI
            website
        """
        self._database = database
        self._data_url = data_url
        self._info_file_url = info_file_url
        self._history_file_url = history_file_url
        self._extract_data()
        self._transform_data()

    def _download_data(self, data_dir):
        ncbi_dir = PROJECT_ROOT / 'data' / 'ncbi'

        logger.info('Downloading Entrez gene info.')
        response = requests.get(self._info_file_url, stream=True)
        if response.status_code == 200:
            version = datetime.today().strftime('%Y%m%d')
            with open(ncbi_dir / 'ncbi_gene_info.gz', 'wb') as f:
                f.write(response.content)
            with gzip.open(ncbi_dir / 'ncbi_gene_info.gz', "rb") as gz:
                with open(ncbi_dir / f"ncbi_info_{version}.tsv",
                          'wb') as f_out:
                    shutil.copyfileobj(gz, f_out)
            remove(ncbi_dir / 'ncbi_gene_info.gz')
        else:
            logger.error(f"Entrez gene info download failed with status code: "
                         f"{response.status_code}")
            raise DownloadException("Entrez gene info download failed")
        response = requests.get(self._history_file_url, stream=True)
        if response.status_code == 200:
            version = datetime.today().strftime('%Y%m%d')
            with open(ncbi_dir / 'ncbi_gene_history.gz', 'wb') as f:
                f.write(response.content)
            with gzip.open(ncbi_dir / 'ncbi_gene_history.gz', "rb") as gz:
                with open(ncbi_dir / f"ncbi_history_{version}.tsv",
                          'wb') as f_out:
                    shutil.copyfileobj(gz, f_out)
            remove(ncbi_dir / 'ncbi_gene_history.gz')
            logger.info('Downloaded Entrez gene history.')
        else:
            logger.error(f"Entrez gene history download failed with status "
                         f"code: {response.status_code}")
            raise DownloadException("Entrez gene history download failed")

    def _files_downloaded(self, data_dir: Path) -> bool:
        """Check whether needed source files exist.

        :param Path data_dir: source data directory
        :return: true if all needed files exist, false otherwise
        """
        files = data_dir.iterdir()

        info_downloaded: bool = False
        history_downloaded: bool = False

        for f in files:
            if f.name.startswith('ncbi_info'):
                info_downloaded = True
            elif f.name.startswith('ncbi_history'):
                history_downloaded = True
        return info_downloaded and history_downloaded

    def _extract_data(self):
        """Gather data from local files or download from source.
        - Data is expected to be in <PROJECT ROOT>/data/ncbi.
        - For now, data files should all be from the same source data version.
        """
        local_data_dir = PROJECT_ROOT / 'data' / 'ncbi'
        local_data_dir.mkdir(exist_ok=True, parents=True)
        if not self._files_downloaded(local_data_dir):
            self._download_data(local_data_dir)
        local_files = [f for f in local_data_dir.iterdir()
                       if f.name.startswith('ncbi')]
        local_files.sort(key=lambda f: f.name.split('_')[-1], reverse=True)
        self._info_src = [f for f in local_files
                          if f.name.startswith('ncbi_info')][0]
        self._history_src = [f for f in local_files
                             if f.name.startswith('ncbi_history')][0]
        self._version = self._info_src.stem.split('_')[-1]

    def _transform_data(self):
        """Modify data and pass to loading functions."""
        self._add_meta()
        # get symbol history
        history_file = open(self._history_src, 'r')
        history = csv.reader(history_file, delimiter='\t')
        next(history)
        prev_symbols = {}
        for row in history:
            if row[0] == '9606' and row[1] != '-':
                gene_id = row[1]
                if gene_id in prev_symbols.keys():
                    prev_symbols[gene_id].append(row[3])
                else:
                    prev_symbols[gene_id] = [row[3]]
        history_file.close()

        # open info file, skip headers
        info_file = open(self._info_src, 'r')
        info = csv.reader(info_file, delimiter='\t')
        next(info)

        with self._database.genes.batch_writer() as batch:
            for row in info:
                is_valid_row = True
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
                            prefix = NamespacePrefix.HGNC.value
                        elif ref.startswith("MIM:"):
                            prefix = NamespacePrefix.OMIM.value
                        elif ref.startswith("IMGT/GENE-DB:"):
                            prefix = NamespacePrefix.IMGT_GENE_DB.value
                        else:
                            prefix = ref.split(':')[0].lower()
                            if prefix not in VALID_CID_PREFIXES:
                                logger.error(f"invalid ref prefix {prefix}"
                                             f" in:\n {row}")
                                is_valid_row = False
                                break
                        other_id = f"{prefix}:{ref.split(':')[-1]}"
                        other_ids.append(other_id)
                    params['other_identifiers'] = other_ids
                else:
                    params['other_identifiers'] = []
                # get label
                if row[8] != '-':
                    params['label'] = row[8]
                # add prev symbols
                if row[1] in prev_symbols.keys():
                    params['previous_symbols'] = prev_symbols[row[1]]
                if is_valid_row:
                    self._load_data(Gene(**params), batch)
        info_file.close()

    def _load_data(self, gene: Gene, batch):
        """Load individual Gene item.

        :param Gene gene: gene instance to load into db
        :param batch: boto3 batch writer
        """
        item = gene.dict()
        concept_id_lower = item['concept_id'].lower()

        if item['symbol']:
            pk = f"{item['symbol'].lower()}##symbol"
            batch.put_item(Item={
                'label_and_type': pk,
                'concept_id': concept_id_lower,
                'src_name': SourceName.NCBI.value
            })
        else:
            del item['symbol']

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

        if item['previous_symbols']:
            item['previous_symbols'] = list(set(item['previous_symbols']))
            item_prev_symbols = {s.lower() for s in item['previous_symbols']}
            for symbol in item_prev_symbols:
                pk = f"{symbol}##prev_symbol"
                batch.put_item(Item={
                    'label_and_type': pk,
                    'concept_id': concept_id_lower,
                    'src_name': SourceName.NCBI.value
                })

        item['label_and_type'] = f"{concept_id_lower}##identity"
        item['src_name'] = SourceName.NCBI.value
        batch.put_item(Item=item)

    def _add_meta(self):
        """Load metadata"""
        metadata = Meta(
            data_license="custom",
            data_license_url="https://www.ncbi.nlm.nih.gov/home/about/policies/",  # noqa: E501
            version=self._version,
            data_url=self._data_url,
            rdp_url="https://reusabledata.org/ncbi-gene.html",
            non_commercial=False,
            share_alike=False,
            attribution=False,
        )
        self._database.metadata.put_item(Item={
            'src_name': SourceName.NCBI.value,
            'data_license': metadata.data_license,
            'data_license_url': metadata.data_license_url,
            'version': metadata.version,
            'data_url': metadata.data_url,
            'rdp_url': metadata.rdp_url,
            'non_commercial': metadata.non_commercial,
            'share_alike': metadata.share_alike,
            'attribution': metadata.attribution,
        })
