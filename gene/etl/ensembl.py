"""This module defines the Ensembl ETL methods."""
from .base import Base
from gene import PROJECT_ROOT, DownloadException
from gene.schemas import SourceName, NamespacePrefix, Strand, Gene, Meta, \
    SequenceLocation, LocationType, IntervalType
import logging
from gene.database import Database
import gffutils
from urllib.request import urlopen
import gzip
from bs4 import BeautifulSoup
import requests
import hashlib
import base64

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class Ensembl(Base):
    """ETL the Ensembl source into the normalized database."""

    def __init__(self,
                 database: Database,
                 data_url='http://ftp.ensembl.org/pub/',
                 gff3_ext='current_gff3/homo_sapiens'
                 ):
        """Initialize Ensembl ETL class.

        :param Database database: DynamoDB database
        :param str data_url: URL to Ensembl's FTP site
        :param str gff3_ext: Extension to Ensembl's current
                             gff3 files for homo sapiens
        """
        self._database = database
        self._data_url = data_url
        self._gff3_url = data_url + gff3_ext
        self._data_file_url = None
        self._version = None
        self._assembly = None
        self._load_data()

    def _get_data_file_url_version(self):
        """Get the most recent version of the gff3 data file."""
        response = requests.get(self._gff3_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [self._gff3_url + '/' + node.get('href')
                     for node in soup.find_all('a')
                     if node.get('href').endswith('gz')]
            self._data_file_url = links[-1]
            fn = self._data_file_url.split('/')[-1]
            self._version = fn.split('.')[2]
            self._assembly = fn.split('.')[1]
        else:
            logger.error(f"Ensembl download failed with status code: "
                         f"{response.status_code}")
            raise DownloadException("Ensembl download failed.")

    def _download_data(self, *args, **kwargs):
        """Download Ensembl GFF3 data file."""
        logger.info('Downloading Ensembl...')
        ens_dir = PROJECT_ROOT / 'data' / 'ensembl'
        ens_dir.mkdir(exist_ok=True, parents=True)
        file_name = ens_dir / f'ensembl_{self._version}.gff3'
        response = urlopen(self._data_file_url)
        with open(file_name, 'wb') as f:
            f.write(gzip.decompress(response.read()))

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

        with self._database.genes.batch_writer() as batch:
            for f in db.all_features():
                if f.attributes.get('ID'):
                    f_id = f.attributes.get('ID')[0].split(':')[0]
                    if f_id == 'gene':
                        gene = self._add_feature(f)
                        if gene:
                            assert Gene(**gene)
                            self._load_symbol(gene, batch)
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

    def _sha512t24u(self, blob):
        """Compute an ASCII digest from binary data.

        :param str blob: binary data
        :return: Binary digest
        """
        digest = hashlib.sha512(blob).digest()
        tdigest = digest[:24]
        tdigest_b64u = base64.urlsafe_b64encode(tdigest).decode("ASCII")
        return tdigest_b64u

    def _add_feature(self, f):
        """Create a gene dictionary.

        :param gffutils.feature.Feature f: A gene from the data
        :return: A gene dictionary if the ID attribute exists.
                 Else return None.
        """
        gene = dict()
        if f.strand == '-':
            gene['strand'] = Strand.REVERSE
        elif f.strand == '+':
            gene['strand'] = Strand.FORWARD
        gene['strand'] = f.strand
        gene['src_name'] = SourceName.ENSEMBL.value

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

        blob = gene['symbol'].encode('utf-8')

        location = {
            "interval": {
                "end": f.end,
                "start": f.start,
                "type": IntervalType.SIMPLE.value
            },
            "sequence_id": f"ga4gh.VSL.{self._sha512t24u(blob)}",
            "type": LocationType.SEQUENCE.value
        }
        assert SequenceLocation(**location)
        gene['location'] = [location]

        gene['label_and_type'] = \
            f"{gene['concept_id'].lower()}##identity"

        return gene

    def _get_other_id_xref(self, src_name, src_id):
        """
        Get other identifier or xref

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
        self._get_data_file_url_version()
        self._download_data()
        self._extract_data()
        self._add_meta()
        self._transform_data()

    def _add_meta(self, *args, **kwargs):
        """Add Ensembl metadata."""
        if self._data_url.startswith("http"):
            self._data_url = f"ftp://{self._data_url.split('://')[-1]}"

        metadata = Meta(
            data_license='custom',
            data_license_url='https://useast.ensembl.org/info/about'
                             '/legal/disclaimer.html',
            version=self._version,
            data_url=self._data_url,
            rdp_url=None,
            non_commercial=False,
            share_alike=False,
            attribution=False,
            assembly=self._assembly
        )

        self._database.metadata.put_item(
            Item={
                'src_name': SourceName.ENSEMBL.value,
                'data_license': metadata.data_license,
                'data_license_url': metadata.data_license_url,
                'version': metadata.version,
                'data_url': metadata.data_url,
                # 'rdp_url': metadata.rdp_url,  # TODO: Add
                'non_commercial': metadata.non_commercial,
                'share_alike': metadata.share_alike,
                'attribution': metadata.attribution,
                'assembly': metadata.assembly
            }
        )
