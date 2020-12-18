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
        self._normalizer_prefixes = self._get_normalizer_prefixes()
        self._extract_data()
        self._transform_data()

    def _download_data(self, data_dir):
        ncbi_dir = PROJECT_ROOT / 'data' / 'ncbi'

        logger.info('Downloading Entrez gene info.')
        for ncbi_type in ['info', 'history']:
            if ncbi_type == 'info':
                response = requests.get(self._info_file_url, stream=True)
            else:
                response = requests.get(self._history_file_url, stream=True)
            if response.status_code == 200:
                version = datetime.today().strftime('%Y%m%d')
                with open(ncbi_dir / f'ncbi_gene_{ncbi_type}.gz', 'wb') as f:
                    f.write(response.content)
                    f.close()
                with gzip.open(
                        ncbi_dir / f'ncbi_gene_{ncbi_type}.gz', "rb") as gz:
                    with open(ncbi_dir / f"ncbi_{ncbi_type}_{version}.tsv",
                              'wb') as f_out:
                        shutil.copyfileobj(gz, f_out)
                        f_out.close()
                remove(ncbi_dir / f'ncbi_gene_{ncbi_type}.gz')
            else:
                logger.error(
                    f"Entrez gene {ncbi_type} download failed with status "
                    f"code: {response.status_code}")
                raise DownloadException(f"Entrez gene {ncbi_type} "
                                        f"download failed")

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
            # Only interested in rows that have homo sapiens tax id
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
                params = dict()
                params['concept_id'] = f"{NamespacePrefix.NCBI.value}:{row[1]}"
                # get symbol
                params['symbol'] = row[2]
                # get aliases
                if row[4] != '-':
                    params['aliases'] = row[4].split('|')
                else:
                    params['aliases'] = []
                # get other identifiers
                if row[5] != '-':
                    params['xrefs'] = []
                    params['other_identifiers'] = []
                    xrefs = row[5].split('|')
                    for ref in xrefs:
                        src = ref.split(':')[0].upper()
                        src_id = ref.split(':')[-1]
                        if src in NamespacePrefix.__members__ and \
                                NamespacePrefix[src].value in \
                                self._normalizer_prefixes:
                            params['other_identifiers'].append(
                                f"{NamespacePrefix[src].value}"
                                f":{src_id}")
                        else:
                            if ref.startswith("MIM:"):
                                prefix = NamespacePrefix.OMIM.value
                            elif ref.startswith("IMGT/GENE-DB:"):
                                prefix = NamespacePrefix.IMGT_GENE_DB.value
                            elif ref.startswith("miRBase:"):
                                prefix = NamespacePrefix.MIRBASE.value
                            params['xrefs'].append(f"{prefix}:{src_id}")
                else:
                    params['xrefs'] = []
                    params['other_identifiers'] = []
                # Get seqid
                if row[6] != '-':
                    if row[6] == 'Un':
                        params['seqid'] = 'unplaced'
                    else:
                        params['seqid'] = row[6]
                # get location
                if row[7] != '-':
                    params['location'] = row[7]
                # get label
                if row[8] != '-':
                    params['label'] = row[8]
                # add prev symbols
                if row[1] in prev_symbols.keys():
                    params['previous_symbols'] = prev_symbols[row[1]]
                else:
                    params['previous_symbols'] = []
                self._load_data(Gene(**params), batch)

    def _load_data(self, gene: Gene, batch):
        """Load individual Gene item.

        :param Gene gene: gene instance to load into db
        :param batch: boto3 batch writer
        """
        item = gene.dict()
        concept_id_lower = item['concept_id'].lower()

        pk = f"{item['symbol'].lower()}##symbol"
        batch.put_item(Item={
            'label_and_type': pk,
            'concept_id': concept_id_lower,
            'src_name': SourceName.NCBI.value
        })

        if item['aliases']:
            item['aliases'] = list(set(item['aliases']))
            aliases = {alias.lower() for alias in item['aliases']}
            for alias in aliases:
                pk = f"{alias}##alias"
                batch.put_item(Item={
                    'label_and_type': pk,
                    'concept_id': concept_id_lower,
                    'src_name': SourceName.NCBI.value
                })
        else:
            del item['aliases']

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
        else:
            del item['previous_symbols']

        if not item['other_identifiers']:
            del item['other_identifiers']

        if not item['xrefs']:
            del item['xrefs']

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
            assembly='GRCh38.p13'
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
