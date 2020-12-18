"""This module defines the HGNC ETL methods."""
from .base import Base
from gene import PROJECT_ROOT, DownloadException
from gene.schemas import SourceName, SymbolStatus, NamespacePrefix
from gene.database import Database
import logging
import json
import requests
from bs4 import BeautifulSoup
import datetime

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class HGNC(Base):
    """ETL the HGNC source into the normalized database."""

    def __init__(self,
                 database: Database,
                 # TODO: Change to ftp
                 data_url='http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/',
                 data_file_ext='json/non_alt_loci_set.json',
                 ):
        """Initialize HGNC ETL class.

        :param Database database: DynamoDB database
        :param str data_url: URL to HGNC's FTP site
        :param str data_file_ext: Extension to HGNC's current JSON data file
                                  for the Non Alt Loci set
        """
        self._database = database
        self._data_url = data_url
        self._data_file_url = data_url + data_file_ext
        self._version = None
        self._normalizer_prefixes = self._get_normalizer_prefixes()
        self._load_data()

    def _download_data(self, *args, **kwargs):
        """Download HGNC JSON data file."""
        logger.info('Downloading HGNC...')
        response = requests.get(self._data_file_url, stream=True)
        if response.status_code == 200:
            r = requests.get(f"{self._data_url}/json/")
        else:
            logger.error(f"HGNC data file download failed with status code: "
                         f"{response.status_code}")
            raise DownloadException("HGNC data file download failed.")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            v_date = soup.find(
                'a', text='non_alt_loci_set.json').next_sibling.split()[0]
            self._version =\
                datetime.datetime.strptime(v_date,
                                           '%d-%b-%Y').strftime('%Y%m%d')

            data_dir = PROJECT_ROOT / 'data' / 'hgnc'
            data_dir.mkdir(exist_ok=True, parents=True)

            with open(f"{PROJECT_ROOT}/data/hgnc/"
                      f"hgnc_{self._version}.json", 'w+') as f:
                f.write(json.dumps(response.json()))

            logger.info('Finished downloading HGNC.')
        else:
            logger.error(f"HGNC download failed with status code: "
                         f"{r.status_code}")
            raise DownloadException("HGNC download failed.")

    def _extract_data(self, *args, **kwargs):
        """Extract data from the HGNC source."""
        if 'data_path' in kwargs:
            self._data_src = kwargs['data_path']
        else:
            hgnc_dir = PROJECT_ROOT / 'data' / 'hgnc'
            self._data_src = sorted(list(hgnc_dir.iterdir()))[-1]

    def _transform_data(self, *args, **kwargs):
        """Transform the HGNC source."""
        with open(self._data_src, 'r') as f:
            data = json.load(f)

        records = data['response']['docs']

        with self._database.genes.batch_writer() as batch:
            for r in records:
                gene = dict()
                gene['concept_id'] = r['hgnc_id'].lower()
                gene['label_and_type'] = \
                    f"{gene['concept_id']}##identity"
                gene['symbol'] = r['symbol']
                gene['label'] = r['name']
                gene['src_name'] = SourceName.HGNC.value
                if r['status']:
                    if r['status'] == 'Approved':
                        gene['symbol_status'] = \
                            SymbolStatus.APPROVED.value
                    elif r['status'] == 'Entry Withdrawn':
                        gene['symbol_status'] =\
                            SymbolStatus.WITHDRAWN.value
                if 'location' in r:
                    gene['location'] = r['location']
                gene['src_name'] = SourceName.HGNC.value
                self._load_other_identifiers(r, gene)
                self._load_approved_symbol(gene, batch)
                self._load_aliases(r, gene, batch)
                self._load_previous_symbols(r, gene, batch)
                batch.put_item(Item=gene)

    def _load_approved_symbol(self, gene, batch):
        """Insert approved symbol data into the database.

        :param dict gene: A transformed gene record
        :param BatchWriter batch: Object to write data to DynamoDB
        """
        symbol = {
            'label_and_type':
                f"{gene['symbol'].lower()}##symbol",
            'concept_id': f"{gene['concept_id']}",
            'src_name': SourceName.HGNC.value
        }
        batch.put_item(Item=symbol)

    def _load_aliases(self, r, gene, batch):
        """Insert alias data into the database.

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        :param BatchWriter batch: Object to write data to DynamoDB
        """
        alias_symbol = list()
        enzyme_id = list()
        if 'alias_symbol' in r:
            alias_symbol = r['alias_symbol']

        if 'enzyme_id' in r:
            enzyme_id = r['enzyme_id']

        gene['aliases'] = list(set(alias_symbol + enzyme_id))
        if gene['aliases']:
            aliases = {t.casefold(): t for t in gene['aliases']}

            for alias in aliases:
                alias = {
                    'label_and_type': f"{alias}##alias",
                    'concept_id': f"{gene['concept_id']}",
                    'src_name': SourceName.HGNC.value
                }
                batch.put_item(Item=alias)
        else:
            del gene['aliases']

    def _load_previous_symbols(self, r, gene, batch):
        """Load previous symbols to a gene record.

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        :param BatchWriter batch: Object to write data to DynamoDB
        """
        if 'prev_symbol' in r:
            prev_symbols = r['prev_symbol']
            gene['previous_symbols'] = list(set(prev_symbols))

            prev_symbols = {t.casefold(): t for t in gene['previous_symbols']}

            for prev_symbol in prev_symbols:
                prev_symbol = {
                    'label_and_type': f"{prev_symbol}##prev_symbol",
                    'concept_id': f"{gene['concept_id']}",
                    'src_name': SourceName.HGNC.value
                }
                batch.put_item(Item=prev_symbol)

    def _load_other_identifiers(self, r, gene):
        """Load other identifiers to a gene record.

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        """
        other_ids = list()
        xrefs = list()
        sources = [
            'entrez_id', 'ensembl_gene_id', 'vega_id', 'ucsc_id', 'ccds_id',
            'uniprot_ids', 'pubmed_id', 'cosmic', 'omim_id', 'mirbase',
            'homeodb', 'snornabase', 'orphanet', 'horde_id', 'merops', 'imgt',
            'iuphar', 'kznf_gene_catalog', 'mamit-trnadb', 'cd', 'lncrnadb',
            'intermediate_filament_db', 'ena', 'pseudogene.org',
            'refseq_accession'
        ]

        for src in sources:
            if src in r:
                if '-' in src:
                    key = src.split('-')[0]
                elif '.' in src:
                    key = src.split('.')[0]
                elif '_' in src:
                    key = src.split("_")[0]
                else:
                    key = src
                if NamespacePrefix[key.upper()]\
                        .value in self._normalizer_prefixes:
                    self._load_other_id_xref(key, src, r, other_ids)
                else:
                    self._load_other_id_xref(key, src, r, xrefs)

        if other_ids:
            gene['other_identifiers'] = other_ids
        if xrefs:
            gene['xrefs'] = xrefs

    def _load_other_id_xref(self, key, src, r, src_type):
        if type(r[src]) == list:
            for other_id in r[src]:
                src_type.append(
                    f"{NamespacePrefix[key.upper()].value}:{other_id}")
        else:
            src_type.append(
                f"{NamespacePrefix[key.upper()].value}"  # noqa: E501
                f":{r[src]}")

    def _load_data(self, *args, **kwargs):
        """Load the HGNC source into normalized database."""
        self._download_data()
        self._extract_data()
        self._transform_data()
        self._add_meta()

    def _add_meta(self, *args, **kwargs):
        """Add HGNC metadata to the gene_metadata table."""
        self._database.metadata.put_item(
            Item={
                'src_name': SourceName.HGNC.value,
                'data_license': 'custom',
                'data_license_url': 'https://www.genenames.org/about/',
                'version': self._version,
                'data_url': self._data_url,
                'rdp_url': None,
                'non_commercial': False,
                'share_alike': False,
                'attribution': False,
            }
        )
