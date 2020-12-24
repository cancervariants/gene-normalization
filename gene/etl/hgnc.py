"""This module defines the HGNC ETL methods."""
from .base import Base
from gene import PROJECT_ROOT, DownloadException
from gene.schemas import SourceName, SymbolStatus, NamespacePrefix, Gene, \
    Meta, ChromosomeLocation, IntervalType, LocationType, Annotation,\
    Chromosome
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
                if 'prev_symbol' in r:
                    self._get_previous_symbols(r, gene)
                if 'location' in r:
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
            'ena', 'pseudogene.org', 'refseq_accession'
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
            if type(r[src]) == str and ':' in r[src]:
                r[src] = r[src].split(':')[-1].strip()
            src_type.append(
                f"{NamespacePrefix[key.upper()].value}"
                f":{r[src]}")

    def _get_location(self, r, gene):
        """Store GA4GH VRS ChromosomeLocation in a gene record.

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        """
        # Get list of a gene's map locations
        if 'and' in r['location']:
            locations = r['location'].split('and')
        else:
            locations = [r['location']]

        location_list = list()
        gene['location_annotations'] = dict()
        for loc in locations:
            loc = loc.strip()
            loc = self._set_annotation(loc, gene)

            if loc:
                if loc == 'mitochondria':
                    gene['location_annotations']['chr'] =\
                        [Chromosome.MITOCHONDRIA.value]
                else:
                    location = dict()
                    interval = dict()
                    self._set_location(loc, location, interval, gene)
                    if location and interval:
                        interval['type'] = IntervalType.CYTOBAND.value
                        location['interval'] = interval
                        location['species_id'] = 'taxonomy:9606'
                        location['type'] = LocationType.CHROMOSOME.value
                        assert ChromosomeLocation(**location)
                        location_list.append(location)

        if location_list:
            gene['locations'] = location_list
        if not gene['location_annotations']:
            del gene['location_annotations']

    def _set_annotation(self, loc, gene):
        """Set the annotations attribute if one is provided.
           Return `True` if a location is provided, `False` otherwise.

        :param str loc: A gene location
        :return: A bool whether or not a gene map location is provided
        """
        annotations = {v.value for v in
                       Annotation.__members__.values()}

        for annotation in annotations:
            if annotation in loc:
                gene['location_annotations']['annotation'] = annotation
                # Check if location is also included
                loc = loc.split(annotation)[0].strip()
                if not loc:
                    return None
        return loc

    def _set_location(self, loc, location, interval, gene):
        """Set a gene's location.

        :param str loc: A gene location
        :param dict location: GA4GH location
        :param dict interval: GA4GH interval
        :param dict gene: A transformed gene record
        """
        arm_match = re.search('[pq]', loc)

        if arm_match:
            # Location gives arm and sub / sub band
            arm_ix = arm_match.start()
            location['chr'] = loc[:arm_ix]

            if '-' in loc:
                # Location gives both start and end
                self._set_interval_range(loc, arm_ix, interval)
            else:
                # Location only gives start
                start = loc[arm_ix:]
                interval['start'] = start
                interval['end'] = start
        else:
            # Only gives chromosome
            if 'chr' in gene['location_annotations']:
                gene['location_annotations']['chr'].append(loc)
            else:
                gene['location_annotations']['chr'] = [loc]

    def _set_interval_range(self, loc, arm_ix, interval):
        """Set the location interval range.

        :param str loc: A gene location
        :param int arm_ix: The index of the q or p arm for a given location
        :param dict interval: The GA4GH interval for a VRS object
        """
        range_ix = re.search('-', loc).start()

        start = loc[arm_ix:range_ix]
        start_arm_ix = re.search("[pq]", start).start()
        start_arm = start[start_arm_ix]

        end = loc[range_ix + 1:]
        end_arm_match = re.search("[pq]", end)

        if not end_arm_match:
            # Does not specify the arm, so use the same as start's
            interval['start'] = start
            interval['end'] = f"{start[0]}{end}"
        else:
            end_arm_ix = end_arm_match.start()
            end_arm = end[end_arm_ix]

            # GA4GH: If start and end are on the same arm,
            # start MUST be the more centromeric position
            if (start_arm == end_arm and end < start) or end_arm == 'p':
                interval['start'] = end
                interval['end'] = start
            elif (start_arm != end_arm and end > start) or end_arm == 'q':
                interval['start'] = start
                interval['end'] = end

    def _load_data(self, *args, **kwargs):
        """Load the HGNC source into normalized database."""
        self._download_data()
        self._extract_data()
        self._add_meta()
        self._transform_data()

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
