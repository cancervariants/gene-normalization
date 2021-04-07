"""This module defines the Ensembl ETL methods."""
from .base import Base
from gene import PROJECT_ROOT
from gene.schemas import SourceName, NamespacePrefix, Strand, Gene, ServiceMeta
import logging
from gene.database import Database
import gffutils
import gzip
from biocommons.seqrepo import SeqRepo
from gene.vrs_locations import SequenceLocation
from ftplib import FTP
import shutil
from os import remove

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class Ensembl(Base):
    """ETL the Ensembl source into the normalized database."""

    def __init__(self,
                 database: Database,
                 data_url='ftp://ftp.ensembl.org/pub/',
                 ):
        """Initialize Ensembl ETL class.

        :param Database database: DynamoDB database
        :param str data_url: URL to Ensembl's FTP site
        """
        self._database = database
        self._sequence_location = SequenceLocation()
        self._data_url = data_url
        self._data_file_url = None
        self._version = '102'
        self._assembly = 'GRCh38'
        self._load_data()

    def _download_data(self):
        """Download Ensembl GFF3 data file."""
        logger.info('Downloading Ensembl...')
        ens_dir = PROJECT_ROOT / 'data' / 'ensembl'
        ens_dir.mkdir(exist_ok=True, parents=True)
        with FTP('ftp.ensembl.org') as ftp:
            ftp.login()
            ftp.cwd('pub/release-102/gff3/homo_sapiens/')
            fn = 'ensembl_102.gff3'
            gz_filepath = ens_dir / f'{fn}.gz'
            with open(gz_filepath, 'wb') as fp:
                ftp.retrbinary('RETR Homo_sapiens.GRCh38.102.gff3.gz',
                               fp.write)
        with gzip.open(gz_filepath, 'rb') as f_in:
            with open(ens_dir / fn, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        remove(gz_filepath)

    def _extract_data(self, *args, **kwargs):
        """Extract data from the Ensembl source."""
        if 'data_path' in kwargs:
            self._data_src = kwargs['data_path']
        else:
            ensembl_dir = PROJECT_ROOT / 'data' / 'ensembl'
            self._data_src = sorted(list(ensembl_dir.iterdir()))[-1]

    def _transform_data(self, *args, **kwargs):
        """Transform the Ensembl source."""
        db = gffutils.create_db(str(self._data_src),
                                dbfn=":memory:",
                                force=True,
                                merge_strategy="create_unique",
                                keep_order=True)

        seqrepo_dir = PROJECT_ROOT / 'data' / 'seqrepo' / '2020-11-27'
        if not seqrepo_dir.exists():
            logger.error("Could not find seqrepo 2020-11-27 directory.")
            raise NotADirectoryError("Could not find seqrepo "
                                     "2020-11-27 directory.")
        sr = SeqRepo(seqrepo_dir)

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
                            assert Gene(**gene)
                            self._load_symbol(gene, batch)
                            self._load_other_ids(gene, batch)
                            batch.put_item(Item=gene)

    def _load_symbol(self, gene, batch):
        """Load symbol records into database.

        :param dict gene: A transformed gene record
        :param BatchWriter batch: Object to write data to DynamoDB
        """
        symbol = {
            'label_and_type': f"{gene['symbol'].lower()}##symbol",
            'concept_id': f"{gene['concept_id'].lower()}",
            'src_name': SourceName.ENSEMBL.value
        }
        batch.put_item(Item=symbol)

    def _load_other_ids(self, gene, batch):
        """Load other identifier records into database.

        :param dict gene: A transformed gene record
        :param BatchWriter batch: Object to write data to DynamoDB
        """
        if 'other_identifiers' in gene and gene['other_identifiers']:
            for other_id in gene['other_identifiers']:
                other_id = {
                    'label_and_type': f"{other_id.lower()}##other_id",
                    'concept_id': f"{gene['concept_id'].lower()}",
                    'src_name': SourceName.ENSEMBL.value
                }
                batch.put_item(Item=other_id)

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

        return gene

    def _add_attributes(self, f, gene):
        """Add concept_id, symbol, and other_identifiers to a gene record.

        :param gffutils.feature.Feature f: A gene from the data
        :param gene: A transformed gene record
        """
        attributes = {
            'ID': 'concept_id',
            'Name': 'symbol',
            'description': 'other_identifiers'
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
                        source = self._get_other_id_xref(src_name, src_id)
                        if 'other_identifiers' in source:
                            gene['other_identifiers'] = \
                                source['other_identifiers']
                        elif 'xrefs' in source:
                            gene['xrefs'] = source['xrefs']
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

    def _get_other_id_xref(self, src_name, src_id):
        """Get other identifier or xref.

        :param str src_name: Source name
        :param src_id: The source's accession number
        :return: A dict containing an other identifier or xref
        """
        source = dict()
        if src_name.startswith('HGNC'):
            source['other_identifiers'] = \
                [f"{NamespacePrefix.HGNC.value}:{src_id}"]
        elif src_name.startswith('NCBI'):
            source['other_identifiers'] = \
                [f"{NamespacePrefix.NCBI.value}:{src_id}"]
        elif src_name.startswith('UniProt'):
            source['xrefs'] = [f"{NamespacePrefix.UNIPROT.value}:{src_id}"]
        elif src_name.startswith('miRBase'):
            source['xrefs'] = [f"{NamespacePrefix.MIRBASE.value}:{src_id}"]
        elif src_name.startswith('RFAM'):
            source['xrefs'] = [f"{NamespacePrefix.RFAM.value}:{src_id}"]
        return source

    def _load_data(self, *args, **kwargs):
        """Load the Ensembl source into normalized database."""
        self._download_data()
        self._extract_data()
        self._add_meta()
        self._transform_data()

    def _add_meta(self, *args, **kwargs):
        """Add Ensembl metadata."""
        metadata = ServiceMeta(
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
