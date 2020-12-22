"""This module defines the HGNC ETL methods."""
from .base import Base
from gene import PROJECT_ROOT, DownloadException
from gene.schemas import SourceName, SymbolStatus, NamespacePrefix, Gene, \
    Meta, ChromosomeLocation, IntervalType, LocationType, Annotation
from gene.database import Database
import logging
import json
import requests
from bs4 import BeautifulSoup
import datetime
import re

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class HGNC(Base):
    """ETL the HGNC source into the normalized database."""

    def __init__(self,
                 database: Database,
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
                gene['src_name'] = SourceName.HGNC.value

                # Store alias, other_identifier,
                # prev_symbols, and location in gene record
                self._get_aliases(r, gene)
                self._get_other_ids_xrefs(r, gene)
                self._get_previous_symbols(r, gene)
                self._get_location(r, gene)

                assert Gene(**gene)
                self._load_dynamodb(gene, batch)

    def _load_dynamodb(self, gene, batch):
        """Insert gene records into DynamoDB gene_concepts table

        :param dict gene: A transformed gene record
        :param BatchWriter batch: Object to write data to DynamoDB
        """
        self._load_approved_symbol(gene, batch)
        self._load_aliases(gene, batch)
        self._load_previous_symbols(gene, batch)
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

    def _get_aliases(self, r, gene):
        """Store aliases in a gene record.

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        """
        alias_symbol = list()
        enzyme_id = list()
        if 'alias_symbol' in r:
            alias_symbol = r['alias_symbol']

        if 'enzyme_id' in r:
            enzyme_id = r['enzyme_id']

        if alias_symbol or enzyme_id:
            gene['aliases'] = list(set(alias_symbol + enzyme_id))

    def _load_aliases(self, gene, batch):
        """Insert alias data into the database.

        :param dict gene: A transformed gene record
        :param BatchWriter batch: Object to write data to DynamoDB
        """
        if 'aliases' in gene:
            aliases = {t.casefold(): t for t in gene['aliases']}

            for alias in aliases:
                alias = {
                    'label_and_type': f"{alias}##alias",
                    'concept_id': f"{gene['concept_id']}",
                    'src_name': SourceName.HGNC.value
                }
                batch.put_item(Item=alias)

    def _get_previous_symbols(self, r, gene):
        """Store previous symbols in a gene record.

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        """
        if 'prev_symbol' in r:
            prev_symbols = r['prev_symbol']
            if prev_symbols:
                gene['previous_symbols'] = list(set(prev_symbols))

    def _load_previous_symbols(self, gene, batch):
        """Load previous symbols to a gene record.

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        :param BatchWriter batch: Object to write data to DynamoDB
        """
        if 'previous_symbols' in gene:
            prev_symbols = {t.casefold(): t for t in gene['previous_symbols']}

            for prev_symbol in prev_symbols:
                prev_symbol = {
                    'label_and_type': f"{prev_symbol}##prev_symbol",
                    'concept_id': f"{gene['concept_id']}",
                    'src_name': SourceName.HGNC.value
                }
                batch.put_item(Item=prev_symbol)

    def _get_other_ids_xrefs(self, r, gene):
        """Store other identifiers and/or xrefs in a gene record.

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
                if key.upper() in NamespacePrefix.__members__:
                    if NamespacePrefix[key.upper()]\
                            .value in self._normalizer_prefixes:
                        self._get_other_id_xref(key, src, r, other_ids)
                    else:
                        self._get_other_id_xref(key, src, r, xrefs)
                else:
                    logger.warning(f"{key} not in schemas.py")

        if other_ids:
            gene['other_identifiers'] = other_ids
        if xrefs:
            gene['xrefs'] = xrefs

    def _get_other_id_xref(self, key, src, r, src_type):
        """Add an other identifier or xref to a gene record.

        :param str key: The source's name
        :param str src: HGNC's source field
        :param dict r: A gene record in the HGNC data file
        :param list src_type: Either other identifiers list or xrefs list
        """
        if type(r[src]) == list:
            for other_id in r[src]:
                src_type.append(
                    f"{NamespacePrefix[key.upper()].value}:{other_id}")
        else:
            src_type.append(
                f"{NamespacePrefix[key.upper()].value}"
                f":{r[src]}")

    def _get_location(self, r, gene):
        """Store location in a gene record.

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        """
        if 'location' in r:
            contains_loc = True
            location = {
                'interval': {
                    'type': IntervalType.CYTOBAND.value
                },
                'species_id': 'taxonomy:9606',
                'type': LocationType.CHROMOSOME.value
            }

            # TODO: Check if this should be included
            #       What to do if includes both location and annotation
            annotations = {v.value for v in Annotation.__members__.values()}
            for annotation in annotations:
                if annotation in r['location']:
                    location['annotation'] = annotation

                    # Check if location is also included
                    r['location'] = r['location'].split(annotation)[0].strip()
                    if not r['location']:
                        contains_loc = False

            if contains_loc:
                arm_match = re.search('[pq]', r['location'])

                if arm_match:
                    # Location gives arm and sub band
                    arm_ix = arm_match.start()
                    location['chr'] = r['location'][:arm_ix]

                    if '-' in r['location']:
                        # Location gives both start and end
                        range_ix = re.search('-', r['location']).start()
                        location['interval']['start'] = \
                            r['location'][arm_ix:range_ix]
                        location['interval']['end'] = \
                            r['location'][range_ix + 1:]
                    else:
                        # Location only gives start
                        start = r['location'][arm_ix:]
                        location['interval']['start'] = start
                else:
                    # Location given is a single chromosome, i.e. 6
                    location['chr'] = r['location']
                    del location['interval']
            else:
                del location['interval']
            assert ChromosomeLocation(**location)
            gene['location'] = [location]

    def _load_data(self, *args, **kwargs):
        """Load the HGNC source into normalized database."""
        self._download_data()
        self._extract_data()
        self._transform_data()
        self._add_meta()

    def _add_meta(self, *args, **kwargs):
        """Add HGNC metadata to the gene_metadata table."""
        if self._data_url.startswith("http"):
            self._data_url = f"ftp://{self._data_url.split('://')[-1]}"

        metadata = Meta(
            data_license='custom',
            data_license_url='https://www.genenames.org/about/',
            version=self._version,
            data_url=self._data_url,
            rdp_url=None,
            non_commercial=False,
            share_alike=False,
            attribution=False
        )

        self._database.metadata.put_item(
            Item={
                'src_name': SourceName.HGNC.value,
                'data_license': metadata.data_license,
                'data_license_url': metadata.data_license_url,
                'version': metadata.version,
                'data_url': metadata.data_url,
                # 'rdp_url': metadata.rdp_url,  # TODO: ADD
                'non_commercial': metadata.non_commercial,
                'share_alike': metadata.share_alike,
                'attribution': metadata.attribution,
            }
        )
