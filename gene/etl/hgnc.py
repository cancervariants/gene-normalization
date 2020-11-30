"""This module defines the HGNC ETL methods."""
from .base import Base
from gene import PROJECT_ROOT
from gene.schemas import SourceName, ApprovalStatus, NamespacePrefix
import logging
import json
import requests
from bs4 import BeautifulSoup
import datetime
from gene.database import GENES_TABLE, METADATA_TABLE

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class HGNC(Base):
    """ETL the HGNC source into the normalized database."""

    def __init__(self,
                 data_url='http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/',
                 data_file_url='http://ftp.ebi.ac.uk/pub/databases/genenames/'
                               'hgnc/json/non_alt_loci_set.json',
                 ):
        """Initialize HGNC ETL class."""
        self._data_url = data_url
        self._data_file_url = data_file_url
        self._version = None
        self._load_data()

    def _download_data(self, *args, **kwargs):
        """Download HGNC JSON data file."""
        logger.info('Downloading HGNC...')
        response = requests.get(self._data_file_url, stream=True)
        r = requests.get(f"{self._data_url}/json/")
        soup = BeautifulSoup(r.text, 'html.parser')
        v_date = soup.find(
            'a', text='non_alt_loci_set.json').next_sibling.split()[0]
        self._version = \
            datetime.datetime.strptime(v_date, '%d-%b-%Y').strftime('%Y%m%d')

        with open(f"{PROJECT_ROOT}/data/hgnc/"
                  f"hgnc_{self._version}.json", 'w+') as f:
            f.write(json.dumps(response.json()))
            f.close()

        logger.info('Finished downloading HGNC.')

    def _extract_data(self, *args, **kwargs):
        """Extract data from the HGNC source."""
        if 'data_path' in kwargs:
            self._data_src = kwargs['data_path']
        else:
            wd_dir = PROJECT_ROOT / 'data' / 'hgnc'
            wd_dir.mkdir(exist_ok=True, parents=True)  # TODO needed?
            try:
                self._data_src = sorted(list(wd_dir.iterdir()))[-1]
            except IndexError:
                raise FileNotFoundError  # TODO HGNC update function here
        pass

    def _transform_data(self, *args, **kwargs):
        """Transform the HGNC source."""
        with open(self._data_src, 'r') as f:
            data = json.load(f)

        records = data['response']['docs']

        with GENES_TABLE.batch_writer() as batch:
            for r in records:
                record = dict()
                record['concept_id'] = r['hgnc_id']
                record['label_and_type'] = f"{record['concept_id']}##identity"
                record['label'] = r['name']
                record['approved_symbol'] = r['symbol']
                if r['status']:
                    if r['status'] == 'Approved':
                        record['approval_status'] = \
                            ApprovalStatus.APPROVED.value
                    elif r['status'] == 'Entry Withdrawn':
                        record['approval_status'] =\
                            ApprovalStatus.WITHDRAWN.value
                record['other_identifiers'] = self._load_other_identifiers(r)
                if 'entrez_id' in r:  # TODO: Include?
                    record['entrez_id'] = r['entrez_id']
                if 'enzyme_id' in r:  # TODO: Include?
                    record['enzyme_id'] = r['enzyme_id']
                symbols = self._load_symbols(r)
                if symbols:
                    record['aliases'] = symbols
                    self._load_aliases(record, batch)
                batch.put_item(Item=record)

    def _load_aliases(self, record, batch):
        """Insert alias data into the database."""
        aliases = set({t.casefold(): t for t in record['aliases']})

        if len(aliases) > 20:
            del record['aliases']
        else:
            for alias in aliases:
                alias = {
                    'label_and_type': f"{alias}##alias",
                    'concept_id': f"{record['concept_id'].lower()}",
                    'src_name': SourceName.HGNC.value
                }
                batch.put_item(Item=alias)

    def _load_symbols(self, record):
        """Load aliases to a record."""
        alias_symbols = list()
        if 'alias_symbol' in record and record['alias_symbol']:
            alias_symbols = record['alias_symbol']

        prev_symbols = list()
        if 'prev_symbol' in record and record['prev_symbol']:
            prev_symbols = record['prev_symbol']

        aliases = alias_symbols + prev_symbols

        if aliases:
            return list(set(aliases))
        return None

    def _load_other_identifiers(self, record):
        """Load other identifiers to a record."""
        other_ids = list()
        sources = [
            'ensembl_gene_id', 'vega_id', 'ucsc_id', 'ccds_id',
            'uniprot_ids', 'pubmed_id', 'cosmic', 'omim_id', 'mirbase',
            'homeodb', 'snornabase', 'orphanet', 'horde_id', 'merops', 'imgt',
            'iuphar', 'kznf_gene_catalog', 'mamit-trnadb', 'cd', 'lncrnadb',
            'intermediate_filament_db'
        ]

        for src in sources:
            if src in record:
                key = src.split("_")[0]
                if type(record[src]) == list:
                    other_ids.append(f"{key}:{record[src][0]}")
                else:
                    if src == 'kznf_gene_catalog':
                        other_ids.append(f"{NamespacePrefix.KZNF_GENE_CATALOG.value}"  # noqa: E501
                                         f":{record[src]}")
                    elif src == 'intermediate_filament_db':
                        other_ids.append(f"{NamespacePrefix.HUMAN_INTERMEDIATE_FILAMENT.value}"  # noqa: E501
                                         f":{record[src]}")
                    elif src == 'mamit-trnadb':
                        other_ids.append(f"{NamespacePrefix.MAMIT_TRNADB.value}"  # noqa: E501
                                         f":{record[src]}")
                    else:
                        other_ids.append(f"{NamespacePrefix[key.upper()].value}"  # noqa: E501
                                         f":{record[src]}")

        return other_ids

    def _load_data(self, *args, **kwargs):
        """Load the HGNC source into normalized database."""
        # self._download_data()
        self._extract_data()
        self._transform_data()
        self._add_meta()

    def _add_meta(self, *args, **kwargs):
        """Add HGNC metadata."""
        METADATA_TABLE.put_item(
            Item={
                'src_name': SourceName.HGNC.value,
                'data_license': '',  # TODO
                'data_license_url': '',  # TODO
                'version': self._version,
                'data_url': self._data_url
            }
        )
