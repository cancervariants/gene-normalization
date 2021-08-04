"""This module defines the Ensembl ETL methods."""
import pydantic

from .base import Base
from gene import PROJECT_ROOT
from gene.schemas import SourceName, NamespacePrefix, Strand, Gene, SourceMeta
import logging
from gene.database import Database
import gffutils
from gene.vrs_locations import SequenceLocation


logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class Ensembl(Base):
    """ETL the Ensembl source into the normalized database."""

    def __init__(self,
                 database: Database,
                 host='ftp.ensembl.org',
                 data_dir='pub/',
                 version=104
                 ):
        """Initialize Ensembl ETL class.

        :param Database database: DynamoDB database
        :param str host: FTP host name
        :param str data_dir: FTP data directory to use
        :param int version: Version for fn
        """
        super().__init__(database, host, data_dir)
        self._sequence_location = SequenceLocation()
        self._host = host
        self._data_dir = data_dir
        self._version = version
        self._fn = f'Homo_sapiens.GRCh38.{self._version}.gff3.gz'
        self._data_url = f"ftp://{self._host}/{self._data_dir}{self._fn}"
        self._data_file_url = None
        self._assembly = 'GRCh38'

    def _download_data(self):
        """Download Ensembl GFF3 data file."""
        logger.info('Downloading Ensembl data file...')
        ens_dir = PROJECT_ROOT / 'data' / 'ensembl'
        ens_dir.mkdir(exist_ok=True, parents=True)
        self._ftp_download(self._host,
                           f'{self._data_dir}release-{self._version}'
                           f'/gff3/homo_sapiens/',
                           f'ensembl_{self._version}.gff3',
                           ens_dir,
                           self._fn)
        logger.info('Successfully downloaded Ensembl data file.')

    def _extract_data(self, *args, **kwargs):
        """Extract data from the Ensembl source."""
        if 'data_path' in kwargs:
            self._data_src = kwargs['data_path']
        else:
            ensembl_dir = PROJECT_ROOT / 'data' / 'ensembl'
            self._data_src = sorted(list(ensembl_dir.iterdir()))[-1]

    def _transform_data(self, *args, **kwargs):
        """Transform the Ensembl source."""
        logger.info('Transforming Ensembl...')
        db = gffutils.create_db(str(self._data_src),
                                dbfn=":memory:",
                                force=True,
                                merge_strategy="create_unique",
                                keep_order=True)

        sr = self.get_seqrepo()

        # Get accession numbers
        accession_numbers = dict()
        for item in db.features_of_type('scaffold'):
            accession_numbers[item[0]] = item[8]['Alias'][-1]
        for item in db.features_of_type('chromosome'):
            accession_numbers[item[0]] = item[8]['Alias'][-1]

        with self._database.genes.batch_writer() as batch:
            for f in db.all_features():
                if f.attributes.get('ID'):
                    f_id = f.attributes.get('ID')[0].split(':')[0]
                    if f_id == 'gene':
                        gene = self._add_gene(f, sr, accession_numbers)
                        if gene:
                            try:
                                assert Gene(**gene)
                            except pydantic.error_wrappers.ValidationError:
                                logger.warning(f"Unable to load gene due to "
                                               f"validation error: {gene}")
                            else:
                                self._load_gene(gene, batch)
        logger.info('Successfully transformed Ensembl.')

    def _add_gene(self, f, sr, accession_numbers):
        """Create a transformed gene record.

        :param gffutils.feature.Feature f: A gene from the data
        :param SeqRepo sr: Access to the seqrepo
        :param dict accession_numbers: Accession numbers for each
            chromosome and scaffold
        :return: A gene dictionary if the ID attribute exists.
                 Else return None.
        """
        gene = dict()
        if f.strand == '-':
            gene['strand'] = Strand.REVERSE
        elif f.strand == '+':
            gene['strand'] = Strand.FORWARD
        gene['src_name'] = SourceName.ENSEMBL.value

        self._add_attributes(f, gene)
        location = self._add_location(f, gene, sr, accession_numbers)
        if location:
            gene['locations'] = [location]

        gene['label_and_type'] = \
            f"{gene['concept_id'].lower()}##identity"
        gene['item_type'] = 'identity'

        return gene

    def _add_attributes(self, f, gene):
        """Add concept_id, symbol, xrefs, and associated_with to a gene record.

        :param gffutils.feature.Feature f: A gene from the data
        :param gene: A transformed gene record
        """
        attributes = {
            'ID': 'concept_id',
            'Name': 'symbol',
            'description': 'xrefs'
        }

        for attribute in f.attributes.items():
            key = attribute[0]

            if key in attributes.keys():
                val = attribute[1]

                if len(val) == 1:
                    val = val[0]
                    if key == 'ID':
                        if val.startswith('gene'):
                            val = f"{NamespacePrefix.ENSEMBL.value}:" \
                                  f"{val.split(':')[1]}"

                if key == 'description':
                    gene['label'] = val.split('[')[0].strip()
                    if 'Source:' in val:
                        src_name = val.split('[')[-1].split(
                            'Source:')[-1].split('Acc')[0].split(';')[0]
                        src_id = val.split('Acc:')[-1].split(']')[0]
                        if ':' in src_id:
                            src_id = src_id.split(':')[-1]
                        source = self._get_xref_associated_with(src_name, src_id)  # noqa: E501
                        if 'xrefs' in source:
                            gene['xrefs'] = source['xrefs']
                        elif 'associated_with' in source:
                            gene['associated_with'] = source['associated_with']
                    continue

                gene[attributes[key]] = val

    def _add_location(self, f, gene, sr, accession_numbers):
        """Add GA4GH SequenceLocation to a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#sequencelocation

        :param gffutils.feature.Feature f: A gene from the data
        :param dict gene: A transformed gene record
        :param dict accession_numbers: Accession numbers for each chromosome
            and scaffold
        :param  SeqRepo sr: Access to the seqrepo
        """
        return self._sequence_location.add_location(accession_numbers[f.seqid],
                                                    f, gene, sr)

    def _get_xref_associated_with(self, src_name, src_id):
        """Get xref or associated_with concept.

        :param str src_name: Source name
        :param src_id: The source's accession number
        :return: A dict containing an other identifier or xref
        """
        source = dict()
        if src_name.startswith('HGNC'):
            source['xrefs'] = \
                [f"{NamespacePrefix.HGNC.value}:{src_id}"]
        elif src_name.startswith('NCBI'):
            source['xrefs'] = \
                [f"{NamespacePrefix.NCBI.value}:{src_id}"]
        elif src_name.startswith('UniProt'):
            source['associated_with'] = [f"{NamespacePrefix.UNIPROT.value}:{src_id}"]  # noqa: E501
        elif src_name.startswith('miRBase'):
            source['associated_with'] = [f"{NamespacePrefix.MIRBASE.value}:{src_id}"]  # noqa: E501
        elif src_name.startswith('RFAM'):
            source['associated_with'] = [f"{NamespacePrefix.RFAM.value}:{src_id}"]  # noqa: E501
        return source

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
        """Add Ensembl metadata."""
        metadata = SourceMeta(
            data_license='custom',
            data_license_url='https://useast.ensembl.org/info/about'
                             '/legal/disclaimer.html',
            version=self._version,
            data_url=self._data_url,
            rdp_url=None,
            data_license_attributes={
                'non_commercial': False,
                'share_alike': False,
                'attribution': False
            },
            genome_assemblies=[self._assembly]
        )

        self._database.metadata.put_item(
            Item={
                'src_name': SourceName.ENSEMBL.value,
                'data_license': metadata.data_license,
                'data_license_url': metadata.data_license_url,
                'version': metadata.version,
                'data_url': metadata.data_url,
                'rdp_url': metadata.rdp_url,
                'data_license_attributes': metadata.data_license_attributes,
                'genome_assemblies': metadata.genome_assemblies
            }
        )

        self._load_meta(self._database, metadata, SourceName.ENSEMBL.value)
