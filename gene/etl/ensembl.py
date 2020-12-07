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
        db = gffutils.create_db(str(self._data_src),
                                dbfn=":memory:",
                                force=True,
                                merge_strategy="create_unique",
                                keep_order=True)

        fields = ['seqid', 'source', 'type', 'start', 'end', 'score',
                  'strand', 'phase', 'attributes']

        for f in db.all_features():
            if f.attributes.get('ID'):
                feature = self._add_feature(f, fields)

                children = db.children(feature['id'])
                del feature['id']
                feature['children'] = list()
                for child in children:
                    feature['children'].append(
                        self._add_feature(child, fields, is_child=True))
                if not feature['children']:
                    del feature['children']

    def _add_feature(self, f, fields, is_child=False):
        """Create a feature dictionary.
        :param gffutils.feature.Feature f: A feature from the data
        :param list fields: A list of possible attribute names
        :param bool is_child: Indicates whether a feature is a child
        :return: A feature dictionary
        """
        feature = dict()
        if not is_child:
            feature['id'] = f.id
        feature['seqid'] = f.seqid
        feature['source'] = f.source
        feature['type'] = f.featuretype
        feature['start'] = f.start
        feature['end'] = f.end
        feature['score'] = f.score
        feature['strand'] = f.strand
        feature['phase'] = f.frame
        feature['attributes'] = list()
        for attribute in f.attributes.items():
            key = attribute[0]
            val = attribute[1]

            if len(val) == 1:
                val = val[0]
                if key == 'ID' or key == 'Parent':
                    if val.startswith('gene') or val.startswith('transcript'):
                        val = val.split(':')[1]

            if key == 'ID':
                key = 'concept_id'
            feature[key] = val

        # Delete empty fields
        for field in fields:
            if feature[field] == '.' or not feature[field]:
                del feature[field]

        return feature

    def _load_data(self, *args, **kwargs):
        """Load the Ensembl source into normalized database."""
        self._download_data()
        self._extract_data()
        self._transform_data()
        # self._add_meta()

    def _add_meta(self, *args, **kwargs):
        """Add Ensembl metadata."""
        self.database.metadata.put_item(
            Item={
                'src_name': SourceName.ENSEMBL.value,
                'data_license': 'temp',
                'data_license_url': 'temp',
                'version': self._version,
                'data_url': self._data_url
            }
        )
