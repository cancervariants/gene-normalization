"""This module defines ETL methods for the NCBI data source."""
from .base import Base
from gene import PROJECT_ROOT, DownloadException
from gene.database import Database
from gene.schemas import Meta, Gene, SourceName, NamespacePrefix, \
    ChromosomeLocation, IntervalType, LocationType, Annotation, Chromosome
import logging
from pathlib import Path
import csv
import requests
from datetime import datetime
import gzip
import shutil
from os import remove
import re

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
                    if not params['xrefs']:
                        del params['xrefs']
                    if not params['other_identifiers']:
                        del params['other_identifiers']
                # get location
                self._get_vrs_location(row, params)
                # get label
                if row[8] != '-':
                    params['label'] = row[8]
                # add prev symbols
                if row[1] in prev_symbols.keys():
                    params['previous_symbols'] = prev_symbols[row[1]]
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

        filtered_item = {k: v for k, v in item.items() if v is not None}
        item.clear()
        item.update(filtered_item)

        item['label_and_type'] = f"{concept_id_lower}##identity"
        item['src_name'] = SourceName.NCBI.value
        batch.put_item(Item=item)

    def _get_vrs_location(self, row, params):
        """Store GA4GH VRS ChromosomeLocation in a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#chromosomelocation

        :param list row: A row in NCBI data file
        :param dict params: A transformed gene record
        """
        params['location_annotations'] = dict()
        chromosomes_locations = self._set_chromsomes_locations(row, params)
        locations = chromosomes_locations['locations']
        chromosomes = chromosomes_locations['chromosomes']

        location_list = list()
        if chromosomes and not locations:
            params['location_annotations']['chr'] = []
            for chromosome in chromosomes:
                if chromosome == 'MT':
                    params['location_annotations'] = {
                        'chr': [Chromosome.MITOCHONDRIA.value]
                    }
                    break

                params['location_annotations']['chr'].append(
                    chromosome.strip())
        elif locations:
            self._add_chromosome_location(locations, location_list, params)
        if location_list:
            params['locations'] = location_list
        if not params['location_annotations']:
            del params['location_annotations']

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

            # NCBI sometimes contains invalid map locations
            if locations:
                invalid_locations = []
                for i in range(len(locations)):
                    loc = locations[i].strip()
                    if not re.match("^([1-9][0-9]?|X[pq]?|Y[pq]?)", loc):
                        logger.info(f'{row[2]} contains invalid map location:'
                                    f'{loc}.')
                        invalid_locations.append(loc)
                        del locations[i]
                if invalid_locations:
                    params['location_annotations']['invalid_locations'] = \
                        invalid_locations

        return {
            'locations': locations,
            'chromosomes': chromosomes
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
            interval = dict()

            if Annotation.ALT_LOC.value in loc:
                loc = loc.split(f"{Annotation.ALT_LOC.value}")[0].strip()
                params['location_annotations']['annotation'] = \
                    Annotation.ALT_LOC.value

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
                        self._set_interval_range(loc, arm_ix, interval)
                    else:
                        # Location only gives start
                        start = loc[arm_ix:]
                        interval['start'] = start
                        interval['end'] = start
                else:
                    # Only arm is included
                    interval['start'] = loc[arm_ix]
                    interval['end'] = loc[arm_ix]
            elif contains_centromere:
                self._set_centromere_location(loc, location, interval)
            else:
                # Location only gives chr
                location = None
                interval = None
                if 'chr' in params['location_annotations']:
                    params['location_annotations']['chr'].append(loc)
                else:
                    params['location_annotations']['chr'] = [loc]

            if location and interval:
                interval['type'] = IntervalType.CYTOBAND.value
                location['interval'] = interval
                location['species_id'] = 'taxonomy:9606'
                location['type'] = LocationType.CHROMOSOME.value
                assert ChromosomeLocation(**location)
                location_list.append(location)

    def _set_interval_range(self, loc, arm_ix, interval):
        """Set the location interval range.

        :param str loc: A gene location
        :param int arm_ix: The index of the q or p arm for a given location
        :param dict interval: The GA4GH interval for a VRS object
        """
        # Location gives both start and end
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
            # https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#cytobandinterval  # noqa: E501
            if (start_arm == end_arm and end < start) or end_arm == 'p':
                interval['start'] = end
                interval['end'] = start
            elif (start_arm != end_arm and end > start) or end_arm == 'q':
                interval['start'] = start
                interval['end'] = end

    def _set_centromere_location(self, loc, location, interval):
        """Set centromere location for a gene.

        :param str loc: A gene location
        :param dict location: GA4GH location
        :param interval: GA4GH interval for a VRS object
        """
        centromere_ix = re.search("cen", loc).start()
        location['chr'] = loc[:centromere_ix].strip()
        interval['start'] = "cen"

        if '-' in loc:
            # Location gives both start and end
            range_ix = re.search('-', loc).start()
            interval['end'] = loc[range_ix + 1:]
        else:
            interval['end'] = "cen"

    def _add_meta(self):
        """Load metadata"""
        if self._data_url.startswith("http"):
            self._data_url = f"ftp://{self._data_url.split('://')[-1]}"

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
            'assembly': metadata.assembly
        })
