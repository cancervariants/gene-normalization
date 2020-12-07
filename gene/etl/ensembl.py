"""This module defines the Ensembl ETL methods."""
from .base import Base
from gene import PROJECT_ROOT
from gene.schemas import SourceName, ApprovalStatus, NamespacePrefix  # noqa: F401, E501
import logging
from gene.database import Database
import gffutils

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class Ensembl(Base):
    """ETL the Ensembl source into the normalized database."""

    def __init__(self,
                 database: Database,
                 data_url='http://ftp.ensembl.org/pub/',
                 data_file_url='http://ftp.ensembl.org/pub/release-102/gff3/'
                               'homo_sapiens/Homo_sapiens.GRCh38.102.gff3.gz'
                 ):
        """Initialize Ensembl ETL class.
        :param Database database: Database object
        :param str data_url: URL to Ensembl's FTP site
        :param str data_file_url: URL to Ensembl  data file
        """
        self.database = database
        self._data_url = data_url
        self._data_file_url = data_file_url
        self._version = '102'
        self._load_data()

    def _download_data(self, *args, **kwargs):
        """Download Ensembl GFF3 data file."""
        # TODO: Site sometimes works, sometimes doesn't.
        pass

    def _extract_data(self, *args, **kwargs):
        """Extract data from the Ensembl source."""
        if 'data_path' in kwargs:
            self._data_src = kwargs['data_path']
        else:
            wd_dir = PROJECT_ROOT / 'data' / 'ensembl'
            wd_dir.mkdir(exist_ok=True, parents=True)  # TODO needed?
            try:
                self._data_src = sorted(list(wd_dir.iterdir()))[-1]
            except IndexError:
                raise FileNotFoundError  # TODO Ensembl update function here
        pass

    def _transform_data(self, *args, **kwargs):
        """Transform the Ensembl source."""
        # db = gffutils.create_db(str(self._data_src),
        #                         dbfn=":memory:",
        #                         force=True,
        #                         merge_strategy="create_unique",
        #                         keep_order=True)

        # TODO: Remove after done testing
        db = gffutils.FeatureDB(f"{PROJECT_ROOT}/data/ensembl/"
                                f"test_ensembl.db", keep_order=True)

        fields = ['seqid', 'start', 'end', 'strand', 'aliases', 'symbol']

        with self.database.genes.batch_writer() as batch:
            for f in db.all_features():
                if f.attributes.get('ID'):
                    f_id = f.attributes.get('ID')[0].split(':')[0]
                    if f_id == 'chromosome' or f_id == 'gene':
                        feature = self._add_feature(f, fields)
                        if feature:
                            if 'aliases' in feature:
                                self._load_alias(feature, batch)
                            if 'symbol' in feature and feature:
                                self._load_symbol(feature, batch)
                            batch.put_item(Item=feature)

    def _load_symbol(self, feature, batch):
        """Load symbol records into database.

        :param dict feature: The feature record
        :param batch_writer batch: Batch writer object
        """
        symbol = {
            'label_and_type': f"{feature['symbol'].lower()}##symbol",
            'concept_id': f"{feature['concept_id'].lower()}",
            'src_name': SourceName.ENSEMBL.value
        }
        batch.put_item(Item=symbol)

    def _load_alias(self, feature, batch):
        """Load alias records into database.

        :param dict feature: The feature record
        :param batch_writer batch: Batch writer object
        """
        aliases = {a.casefold(): a for a in feature['aliases']}
        if len(aliases) > 20:
            del feature['aliases']
        else:
            for alias in aliases:
                alias = {
                    'label_and_type': f"{alias}##alias",
                    'concept_id': f"{feature['concept_id'].lower()}",
                    'src_name': SourceName.ENSEMBL.value
                }
                batch.put_item(Item=alias)

    def _add_feature(self, f, fields):
        """Create a feature dictionary.

        :param gffutils.feature.Feature f: A feature from the data
        :param list fields: A list of possible attribute names
        :return: A feature dictionary if the ID attribute exists.
                 Else return None.
        """
        feature = dict()
        feature['seqid'] = f.seqid
        feature['start'] = f.start
        feature['stop'] = f.end
        feature['strand'] = f.strand
        feature['attributes'] = list()

        attributes = {
            'Alias': 'aliases',
            'ID': 'concept_id',
            'Name': 'symbol',
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

                feature[attributes[key]] = val

        if 'concept_id' not in feature:
            return None

        # Delete empty fields
        for field in fields:
            if field in feature:
                if feature[field] == '.' or not feature[field]:
                    del feature[field]

        feature['label_and_type'] = \
            f"{feature['concept_id'].lower().split('##')[0]}##identity"

        return feature

    def _load_data(self, *args, **kwargs):
        """Load the Ensembl source into normalized database."""
        self._download_data()
        self._extract_data()
        self._transform_data()
        self._add_meta()

    def _add_meta(self, *args, **kwargs):
        """Add Ensembl metadata."""
        # TODO: Add license info
        self.database.metadata.put_item(
            Item={
                'src_name': SourceName.ENSEMBL.value,
                'data_license': 'temp',
                'data_license_url': 'temp',
                'version': self._version,
                'data_url': self._data_url
            }
        )
