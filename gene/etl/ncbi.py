"""This module defines ETL methods for the NCBI data source."""
from .base import Base
from gene import PROJECT_ROOT, PREFIX_LOOKUP
from gene.database import Database
from gene.schemas import SourceMeta, Gene, SourceName, NamespacePrefix, \
    Annotation, Chromosome, SymbolStatus
import logging
from pathlib import Path
import csv
from datetime import datetime
import re
import gffutils
from gene.vrs_locations import SequenceLocation, ChromosomeLocation


logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class NCBI(Base):
    """ETL class for NCBI source"""

    def __init__(self,
                 database: Database,
                 host='ftp.ncbi.nlm.nih.gov',
                 data_dir='gene/DATA/',
                 assembly: str = 'GRCh38.p13'):
        """Construct the NCBI ETL instance.

        :param Database database: gene database for adding new data
        :param str host: FTP host name
        :param str data_dir: FTP data directory to use
        :param str assembly: The genome assembly
        """
        super().__init__(database, host, data_dir)
        self._sequence_location = SequenceLocation()
        self._chromosome_location = ChromosomeLocation()
        self._data_url = f"ftp://{host}"
        self._assembly = assembly
        self._date_today = datetime.today().strftime('%Y%m%d')

    def perform_etl(self):
        """Perform ETL methods.

        :return: Concept IDs of concepts successfully loaded
        """
        self._extract_data()
        self._transform_data()
        self._database.flush_batch()
        return self._processed_ids

    def _download_data(self, ncbi_dir: Path):
        """Download NCBI info, history, and GRCh38 files.

        :param str ncbi_dir: The NCBI data directory
        """
        # Download info
        data_dir = f'{self._data_dir}GENE_INFO/Mammalia/'
        fn = f'ncbi_info_{self._date_today}.tsv'
        data_fn = 'Homo_sapiens.gene_info.gz'
        logger.info('Downloading NCBI gene_info....')
        self._ftp_download(self._host, data_dir, fn, ncbi_dir, data_fn)
        logger.info('Successfully downloaded NCBI gene_info.')

        # Download history
        fn = f'ncbi_history_{self._date_today}.tsv'
        data_fn = 'gene_history.gz'
        logger.info('Downloading NCBI gene_history...')
        self._ftp_download(self._host, self._data_dir, fn, ncbi_dir, data_fn)
        logger.info('Successfully downloaded NCBI gene_history.')

        # Download gff
        og_fn = 'GCF_000001405.39_GRCh38.p13'
        data_dir = 'genomes/refseq/vertebrate_mammalian/Homo_sapiens/' \
                   f'latest_assembly_versions/{og_fn}/'
        fn = f'ncbi_{self._assembly}.gff'
        data_fn = f'{og_fn}_genomic.gff.gz'
        logger.info('Downloading NCBI gff data file...')
        self._ftp_download(self._host, data_dir, fn, ncbi_dir, data_fn)
        logger.info('Successfully downloaded NCBI gff data file.')

    def _files_downloaded(self, data_dir: Path) -> bool:
        """Check whether needed source files exist.

        :param Path data_dir: source data directory
        :return: true if all needed files exist, false otherwise
        """
        files = data_dir.iterdir()

        info_downloaded: bool = False
        history_downloaded: bool = False
        gff_downloaded: bool = False

        for f in files:
            if f.name.startswith(f'ncbi_info_{self._date_today}'):
                info_downloaded = True
            elif f.name.startswith(f'ncbi_history_{self._date_today}'):
                history_downloaded = True
            elif f.name.startswith('ncbi_GRCh38.p13'):
                gff_downloaded = True
        return info_downloaded and history_downloaded and gff_downloaded

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
        self._gff_src = [f for f in local_files
                         if f.name.startswith('ncbi_GRCh')][0]
        self._version = self._info_src.stem.split('_')[-1]

    def _get_prev_symbols(self):
        """Store a gene's symbol history.

        :return: A dictionary of a gene's previous symbols
        """
        # get symbol history
        history_file = open(self._history_src, 'r')
        history = csv.reader(history_file, delimiter='\t')
        next(history)
        prev_symbols = {}
        with self._database.genes.batch_writer() as batch:
            for row in history:
                # Only interested in rows that have homo sapiens tax id
                if row[0] == '9606':
                    if row[1] != '-':
                        gene_id = row[1]
                        if gene_id in prev_symbols.keys():
                            prev_symbols[gene_id].append(row[3])
                        else:
                            prev_symbols[gene_id] = [row[3]]
                    else:
                        # Load discontinued genes
                        params = {
                            'concept_id':
                                f'{NamespacePrefix.NCBI.value.lower()}:'
                                f'{row[2]}',
                            'symbol': row[3],
                            'symbol_status': SymbolStatus.DISCONTINUED.value
                        }
                        assert Gene(**params)
                        self._load_gene(params, batch)
        history_file.close()
        return prev_symbols

    def _add_xrefs_associated_with(self, val, params):
        """Add xrefs and associated_with refs to a transformed gene.

        :param list val: A list of source ids for a given gene
        :param dict params: A transformed gene record
        """
        params['xrefs'] = []
        params['associated_with'] = []
        for src in val:
            src_name = src.split(':')[0].upper()
            src_id = src.split(':')[-1]
            if src_name == "GENEID":
                params['concept_id'] = f"{NamespacePrefix.NCBI.value}:{src_id}"
            elif src_name in NamespacePrefix.__members__ and \
                    NamespacePrefix[src_name].value in PREFIX_LOOKUP:
                params['xrefs'].append(
                    f"{NamespacePrefix[src_name].value}"
                    f":{src_id}")
            else:
                if src_name.startswith("MIM"):
                    prefix = NamespacePrefix.OMIM.value
                elif src_name.startswith("IMGT/GENE-DB"):
                    prefix = NamespacePrefix.IMGT_GENE_DB.value
                elif src_name.startswith("MIRBASE"):
                    prefix = NamespacePrefix.MIRBASE.value
                else:
                    prefix = None
                if prefix:
                    params['associated_with'].append(f"{prefix}:{src_id}")
                else:
                    logger.info(f"{src_name} is not in NameSpacePrefix.")
        if not params['xrefs']:
            del params['xrefs']
        if not params['associated_with']:
            del params['associated_with']

    def _get_gene_info(self, prev_symbols):
        """Store genes from NCBI info file.

        :param dict prev_symbols: A dictionary of a gene's previous symbols
        :return: A dictionary of gene's from the NCBI info file.
        """
        # open info file, skip headers
        info_file = open(self._info_src, 'r')
        info = csv.reader(info_file, delimiter='\t')
        next(info)

        info_genes = dict()
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
            # get associated_with
            if row[5] != '-':
                associated_with = row[5].split('|')
                self._add_xrefs_associated_with(associated_with, params)
            # get chromosome location
            vrs_chr_location = self._get_vrs_chr_location(row, params)
            if 'exclude' in vrs_chr_location:
                # Exclude genes with multiple distinct locations (e.g. OMS)
                continue
            if not vrs_chr_location:
                vrs_chr_location = []
            params['locations'] = vrs_chr_location
            # get label
            if row[8] != '-':
                params['label'] = row[8]
            # add prev symbols
            if row[1] in prev_symbols.keys():
                params['previous_symbols'] = prev_symbols[row[1]]
            info_genes[params['symbol']] = params
        return info_genes

    def _get_gene_gff(self, db, info_genes, sr):
        """Store genes from NCBI gff file.

        :param FeatureDB db: GFF database
        :param dict info_genes: A dictionary of gene's from the NCBI info file.
        :param SeqRepo sr: Access to the seqrepo
        """
        for f in db.all_features():
            if f.attributes.get('ID'):
                f_id = f.attributes.get('ID')[0]
                if f_id.startswith('gene'):
                    symbol = f.attributes['Name'][0]
                    if symbol in info_genes:
                        # Just need to add SequenceLocation
                        params = info_genes.get(symbol)
                        vrs_sq_location = \
                            self._get_vrs_sq_location(db, sr, params, f_id)
                        if vrs_sq_location:
                            params['locations'].append(vrs_sq_location)
                    else:
                        # Need to add entire gene
                        gene = self._add_gff_gene(db, f, sr, f_id)
                        info_genes[gene['symbol']] = gene

    def _add_gff_gene(self, db, f, sr, f_id):
        """Create a transformed gene recor from NCBI gff file.

        :param FeatureDB db: GFF database
        :param Feature f: A gene from the gff data file
        :param SeqRepo sr: Access to the seqrepo
        :param str f_id: The feature's ID
        :return: A gene dictionary if the ID attribute exists.
                 Else return None.
        """
        params = dict()
        params['src_name'] = SourceName.NCBI.value
        self._add_attributes(f, params)
        sq_loc = self._get_vrs_sq_location(db, sr, params, f_id)
        if sq_loc:
            params['locations'] = [sq_loc]
        else:
            params['locations'] = list()
        params['label_and_type'] = \
            f"{params['concept_id'].lower()}##identity"
        return params

    def _add_attributes(self, f, gene):
        """Add concept_id, symbol, and xrefs/associated_with to a gene record.

        :param gffutils.feature.Feature f: A gene from the data
        :param gene: A transformed gene record
        """
        attributes = ['ID', 'Name', 'description', 'Dbxref']

        for attribute in f.attributes.items():
            key = attribute[0]
            if key in attributes:
                val = attribute[1]

                if len(val) == 1 and key != 'Dbxref':
                    val = val[0]

                if key == 'Dbxref':
                    self._add_xrefs_associated_with(val, gene)
                elif key == 'Name':
                    gene['symbol'] = val

    def _get_vrs_sq_location(self, db, sr, params, f_id):
        """Store GA4GH VRS SequenceLocation in a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#sequencelocation

        :param FeatureDB db: GFF database
        :param SeqRepo sr: Access to the seqrepo
        :param dict params: A transformed gene record
        :param str f_id: The feature's ID
        :return: A GA4GH VRS SequenceLocation
        """
        gene = db[f_id]
        params['strand'] = gene.strand
        return self._sequence_location.add_location(gene.seqid, gene,
                                                    params, sr)

    def _get_xref_associated_with(self, src_name, src_id):
        """Get xref or associated_with ref.

        :param str src_name: Source name
        :param src_id: The source's accession number
        :return: A dict containing an xref or associated_with ref
        """
        source = dict()
        if src_name.startswith('HGNC'):
            source['xrefs'] = \
                [f"{NamespacePrefix.HGNC.value}:{src_id}"]
        elif src_name.startswith('NCBI'):
            source['xrefs'] = \
                [f"{NamespacePrefix.NCBI.value}:{src_id}"]
        elif src_name.startswith('UniProt'):
            source['associated_with'] = [f"{NamespacePrefix.UNIPROT.value}:{src_id}"]  # noqa E501
        elif src_name.startswith('miRBase'):
            source['associated_with'] = [f"{NamespacePrefix.MIRBASE.value}:{src_id}"]  # noqa E501
        elif src_name.startswith('RFAM'):
            source['associated_with'] = [f"{NamespacePrefix.RFAM.value}:{src_id}"]  # noqa E501
        return source

    def _get_vrs_chr_location(self, row, params):
        """Store GA4GH VRS ChromosomeLocation in a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#chromosomelocation

        :param list row: A row in NCBI data file
        :param dict params: A transformed gene record
        :return: A list of GA4GH VRS ChromosomeLocations
        """
        params['location_annotations'] = list()
        chromosomes_locations = self._set_chromsomes_locations(row, params)
        locations = chromosomes_locations['locations']
        chromosomes = chromosomes_locations['chromosomes']
        if chromosomes_locations['exclude']:
            return ['exclude']

        location_list = list()
        if chromosomes and not locations:
            for chromosome in chromosomes:
                if chromosome == 'MT':
                    params['location_annotations'].append(
                        Chromosome.MITOCHONDRIA.value)
                else:
                    params['location_annotations'].append(chromosome.strip())
        elif locations:
            self._add_chromosome_location(locations, location_list, params)
        if not params['location_annotations']:
            del params['location_annotations']
        return location_list

    def _set_chromsomes_locations(self, row, params):
        """Set chromosomes and locations for a given gene record.

        :param list row: A gene row in the NCBI data file
        :param dict params: A transformed gene record
        :return: A dictionary containing a gene's chromosomes and locations
        """
        chromosomes = None
        if row[6] != '-':
            if '|' in row[6]:
                chromosomes = row[6].split('|')
            else:
                chromosomes = [row[6]]

            if len(chromosomes) >= 2:
                if chromosomes and 'X' not in chromosomes and \
                        'Y' not in chromosomes:
                    logger.info(f'{row[2]} contains multiple distinct '
                                f'chromosomes: {chromosomes}.')
                    chromosomes = None

        locations = None
        exclude = False
        if row[7] != '-':
            if '|' in row[7]:
                locations = row[7].split('|')
            elif ';' in row[7]:
                locations = row[7].split(';')
            elif 'and' in row[7]:
                locations = row[7].split('and')
            else:
                locations = [row[7]]

            # Sometimes locations will store the same location twice
            if len(locations) == 2:
                if locations[0] == locations[1]:
                    locations = [locations[0]]

            # Exclude genes where there are multiple distinct locations
            # i.e. OMS: '10q26.3', '19q13.42-q13.43', '3p25.3'
            if len(locations) > 2:
                logger.info(f'{row[2]} contains multiple distinct '
                            f'locations: {locations}.')
                locations = None
                exclude = True

            # NCBI sometimes contains invalid map locations
            if locations:
                for i in range(len(locations)):
                    loc = locations[i].strip()
                    if not re.match("^([1-9][0-9]?|X[pq]?|Y[pq]?)", loc):
                        logger.info(f'{row[2]} contains invalid map location:'
                                    f'{loc}.')
                        params['location_annotations'].append(loc)
                        del locations[i]
        return {
            'locations': locations,
            'chromosomes': chromosomes,
            'exclude': exclude
        }

    def _add_chromosome_location(self, locations, location_list, params):
        """Add a chromosome location to the location list.

        :param list locations: NCBI map locations for a gene record.
        :param list location_list: A list to store chromosome locations.
        :param dict params: A transformed gene record
        """
        for i in range(len(locations)):
            loc = locations[i].strip()
            location = dict()

            if Annotation.ALT_LOC.value in loc:
                loc = loc.split(f"{Annotation.ALT_LOC.value}")[0].strip()
                params['location_annotations'].append(Annotation.ALT_LOC.value)

            contains_centromere = False
            if 'cen' in loc:
                contains_centromere = True

            arm_match = re.search("[pq]", loc)
            if arm_match and not contains_centromere:
                arm_ix = arm_match.start()
                chromosome = loc[:arm_ix].strip()

                # NCBI sometimes stores invalid map locations
                # i.e. 7637 stores 'map from Rosati ref via FISH [AFS]'
                if not re.match("^([1-9][0-9]?|X|Y|MT)$", chromosome):
                    continue
                location['chr'] = chromosome

                # Check to see if there is a band / sub band included
                if arm_ix != len(loc) - 1:
                    if '-' in loc:
                        self._chromosome_location.set_interval_range(loc,
                                                                     arm_ix,
                                                                     location)
                    else:
                        # Location only gives start
                        start = loc[arm_ix:]
                        location['start'] = start
                        location['end'] = start
                else:
                    # Only arm is included
                    location['start'] = loc[arm_ix]
                    location['end'] = loc[arm_ix]
            elif contains_centromere:
                self._set_centromere_location(loc, location)
            else:
                # Location only gives chr
                params['location_annotations'].append(loc)

            chr_location = \
                self._chromosome_location.get_location(location, params)
            if chr_location:
                location_list.append(chr_location)

    def _set_centromere_location(self, loc, location):
        """Set centromere location for a gene.

        :param str loc: A gene location
        :param dict location: GA4GH location
        """
        centromere_ix = re.search("cen", loc).start()
        if '-' in loc:
            # Location gives both start and end
            range_ix = re.search('-', loc).start()
            if 'q' in loc:
                location['chr'] = loc[:centromere_ix].strip()
                location['start'] = "cen"
                location['end'] = loc[range_ix + 1:]
            elif 'p' in loc:
                p_ix = re.search("p", loc).start()
                location['chr'] = loc[:p_ix].strip()
                location['end'] = "cen"
                location['start'] = loc[:range_ix]
        else:
            location['chr'] = loc[:centromere_ix].strip()
            location['start'] = "cen"
            location['end'] = "cen"

    def _transform_data(self):
        """Modify data and pass to loading functions."""
        logger.info('Transforming NCBI...')
        self._add_meta()
        prev_symbols = self._get_prev_symbols()
        info_genes = self._get_gene_info(prev_symbols)

        sr = self.get_seqrepo()

        # create db for gff file
        db = gffutils.create_db(str(self._gff_src),
                                dbfn=":memory:",
                                force=True,
                                merge_strategy="create_unique",
                                keep_order=True)

        self._get_gene_gff(db, info_genes, sr)

        with self._database.genes.batch_writer() as batch:
            for gene in info_genes.keys():
                assert Gene(**info_genes[gene])
                self._load_gene(info_genes[gene], batch)
        logger.info('Successfully transformed NCBI.')

    def _add_meta(self):
        """Load metadata"""
        metadata = SourceMeta(
            data_license="custom",
            data_license_url="https://www.ncbi.nlm.nih.gov/home/"
                             "about/policies/",
            version=self._version,
            data_url=self._data_url,
            rdp_url="https://reusabledata.org/ncbi-gene.html",
            data_license_attributes={
                'non_commercial': False,
                'share_alike': False,
                'attribution': False
            },
            genome_assemblies=[self._assembly]
        )

        self._load_meta(self._database, metadata, SourceName.NCBI.value)
