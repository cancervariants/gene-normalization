"""This module defines the HGNC ETL methods."""
from .base import Base
from gene import PROJECT_ROOT, PREFIX_LOOKUP
from gene.schemas import SourceName, SymbolStatus, NamespacePrefix, \
    SourceMeta, Annotation, Chromosome
from gene.database import Database
import logging
import json
import shutil
import re
from gene.vrs_locations import ChromosomeLocation

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class HGNC(Base):
    """ETL the HGNC source into the normalized database."""

    def __init__(self,
                 database: Database,
                 host='ftp.ebi.ac.uk',
                 data_dir='pub/databases/genenames/hgnc/json/',
                 fn='hgnc_complete_set.json'
                 ):
        """Initialize HGNC ETL class.

        :param Database database: DynamoDB database
        :param str host: FTP host name
        :param str data_dir: FTP data directory to use
        :param str fn: Data file to download
        """
        super().__init__(database, host, data_dir)
        self._chromosome_location = ChromosomeLocation()
        self._data_url = f"ftp://{host}/{data_dir}{fn}"
        self._fn = fn
        self._version = None

    def _download_data(self, *args, **kwargs):
        """Download HGNC JSON data file."""
        logger.info('Downloading HGNC data file...')
        hgnc_data_dir = PROJECT_ROOT / 'data' / 'hgnc'
        hgnc_data_dir.mkdir(exist_ok=True, parents=True)
        tmp_fn = 'hgnc_version.json'
        self._version = \
            self._ftp_download(self._host, self._data_dir, tmp_fn,
                               hgnc_data_dir, self._fn)
        shutil.move(f"{hgnc_data_dir}/{tmp_fn}",
                    f"{hgnc_data_dir}/hgnc_{self._version}.json")
        logger.info('Successfully downloaded HGNC data file.')

    def _extract_data(self, *args, **kwargs):
        """Extract data from the HGNC source."""
        if 'data_path' in kwargs:
            self._data_src = kwargs['data_path']
        else:
            hgnc_dir = PROJECT_ROOT / 'data' / 'hgnc'
            self._data_src = sorted(list(hgnc_dir.iterdir()))[-1]

    def _transform_data(self, *args, **kwargs):
        """Transform the HGNC source."""
        logger.info('Transforming HGNC...')
        with open(self._data_src, 'r') as f:
            data = json.load(f)

        records = data['response']['docs']

        with self._database.genes.batch_writer() as batch:
            for r in records:
                gene = dict()
                gene['concept_id'] = r['hgnc_id'].lower()
                gene['label_and_type'] = \
                    f"{gene['concept_id']}##identity"
                gene['item_type'] = 'identity'
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

                # store alias, xref, associated_with, prev_symbols, location
                self._get_aliases(r, gene)
                self._get_xrefs_associated_with(r, gene)
                if 'prev_symbol' in r:
                    self._get_previous_symbols(r, gene)
                if 'location' in r:
                    self._get_location(r, gene)
                self._load_gene(gene, batch)
        logger.info('Successfully transformed HGNC.')

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

    def _get_previous_symbols(self, r, gene):
        """Store previous symbols in a gene record.

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        """
        prev_symbols = r['prev_symbol']
        if prev_symbols:
            gene['previous_symbols'] = list(set(prev_symbols))

    def _get_xrefs_associated_with(self, r, gene):
        """Store xrefs and/or associated_with refs in a gene record.

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        """
        xrefs = list()
        associated_with = list()
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
                    if NamespacePrefix[key.upper()].value \
                            in PREFIX_LOOKUP.keys():
                        self._get_xref_associated_with(key, src, r, xrefs)
                    else:
                        self._get_xref_associated_with(key, src, r,
                                                       associated_with)
                else:
                    logger.warning(f"{key} not in schemas.py")

        if xrefs:
            gene['xrefs'] = xrefs
        if associated_with:
            gene['associated_with'] = associated_with

    def _get_xref_associated_with(self, key, src, r, src_type):
        """Add an xref or associated_with ref to a gene record.

        :param str key: The source's name
        :param str src: HGNC's source field
        :param dict r: A gene record in the HGNC data file
        :param list src_type: Either xrefs or associated_with list
        """
        if type(r[src]) == list:
            for xref in r[src]:
                src_type.append(
                    f"{NamespacePrefix[key.upper()].value}:{xref}")
        else:
            if isinstance(r[src], str) and ':' in r[src]:
                r[src] = r[src].split(':')[-1].strip()
            src_type.append(
                f"{NamespacePrefix[key.upper()].value}"
                f":{r[src]}")

    def _get_location(self, r, gene):
        """Store GA4GH VRS ChromosomeLocation in a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#chromosomelocation

        :param dict r: A gene record in the HGNC data file
        :param dict gene: A transformed gene record
        """
        # Get list of a gene's map locations
        if 'and' in r['location']:
            locations = r['location'].split('and')
        else:
            locations = [r['location']]

        location_list = list()
        gene['location_annotations'] = list()
        for loc in locations:
            loc = loc.strip()
            loc = self._set_annotation(loc, gene)

            if loc:
                if loc == 'mitochondria':
                    gene['location_annotations'].append(
                        Chromosome.MITOCHONDRIA.value)
                else:
                    location = dict()
                    self._set_location(loc, location, gene)
                    chr_location = \
                        self._chromosome_location.get_location(location, gene)
                    if chr_location:
                        location_list.append(chr_location)

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
                gene['location_annotations'].append(annotation)
                # Check if location is also included
                loc = loc.split(annotation)[0].strip()
                if not loc:
                    return None
        return loc

    def _set_location(self, loc, location, gene):
        """Set a gene's location.

        :param str loc: A gene location
        :param dict location: GA4GH location
        :param dict gene: A transformed gene record
        """
        arm_match = re.search('[pq]', loc)

        if arm_match:
            # Location gives arm and sub / sub band
            arm_ix = arm_match.start()
            location['chr'] = loc[:arm_ix]

            if '-' in loc:
                # Location gives both start and end
                self._chromosome_location.set_interval_range(loc,
                                                             arm_ix, location)
            else:
                # Location only gives start
                start = loc[arm_ix:]
                location['start'] = start
                location['end'] = start
        else:
            # Only gives chromosome
            gene['location_annotations'].append(loc)

    def perform_etl(self, *args, **kwargs):
        """Extract, Transform, and Load data into DynamoDB database.

        :return: Concept IDs of concepts successfully loaded
        """
        self._download_data()
        self._extract_data()
        self._add_meta()
        self._transform_data()
        self._database.flush_batch()
        return self._processed_ids

    def _add_meta(self, *args, **kwargs):
        """Add HGNC metadata to the gene_metadata table."""
        metadata = SourceMeta(
            data_license='custom',
            data_license_url='https://www.genenames.org/about/',
            version=self._version,
            data_url=self._data_url,
            rdp_url=None,
            data_license_attributes={
                'non_commercial': False,
                'share_alike': False,
                'attribution': False
            },
            genome_assemblies=[]
        )

        self._load_meta(self._database, metadata, SourceName.HGNC.value)
