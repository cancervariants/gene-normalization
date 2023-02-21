"""A base class for extraction, transformation, and loading of data."""
from abc import ABC, abstractmethod
from typing import Optional, List
from gene.database import AbstractDatabase
from gene import ITEM_TYPES, SEQREPO_DATA_PATH
from biocommons.seqrepo import SeqRepo
from pathlib import Path
from ftplib import FTP
import gzip
import shutil
from os import remove
from dateutil import parser
import datetime
import logging
import pydantic
from gene.schemas import Gene, MatchType, SourceName

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class Base(ABC):
    """The ETL base class."""

    def __init__(self, database: AbstractDatabase, data_host: str, data_dir: str,
                 src_data_dir: Path,
                 seqrepo_dir=SEQREPO_DATA_PATH,
                 *args, **kwargs) -> None:
        """Instantiate Base class.

        :param Database database: DynamoDB database
        :param str host: Hostname of FTP site
        :param str data_dir: Data directory of FTP site to look at
        :param Path src_data_dir: Data directory for source
        :param Path seqrepo_dir: Path to seqrepo directory
        """
        self._src_name = SourceName(self.__class__.__name__)
        self._database = database
        self._data_host = data_host
        self._data_dir = data_dir
        self.src_data_dir = src_data_dir
        self._processed_ids = list()
        self.seqrepo = self.get_seqrepo(seqrepo_dir)

    @abstractmethod
    def perform_etl(self) -> List[str]:
        """Extract, Transform, and Load data into DynamoDB database.

        :return: Concept IDs of concepts successfully loaded
        """
        raise NotImplementedError

    @abstractmethod
    def _extract_data(self, *args, **kwargs) -> None:
        """Extract data from FTP site or local data directory."""
        raise NotImplementedError

    @abstractmethod
    def _transform_data(self, *args, **kwargs) -> None:
        """Transform data to model."""
        raise NotImplementedError

    @abstractmethod
    def _add_meta(self, *args, **kwargs) -> None:
        """Add source meta to DynamoDB table."""
        raise NotImplementedError

    def _create_data_directory(self):
        """Create data directory for source."""
        self.src_data_dir.mkdir(exist_ok=True, parents=True)

    def _load_gene(self, gene) -> None:
        """Load a gene record into database. This method takes responsibility for:
         * validating structure correctness
         * removing duplicates from list-like fields
         * removing empty fields

        :param dict gene: Gene record
        """
        try:
            assert Gene(match_type=MatchType.NO_MATCH, **gene)
        except pydantic.error_wrappers.ValidationError as e:
            logger.warning(f"Unable to load {gene} due to validation error: "
                           f"{e}")
        else:
            concept_id = gene['concept_id'].lower()
            gene['label_and_type'] = f"{concept_id}##identity"
            gene["src_name"] = self._src_name.value
            gene['item_type'] = 'identity'

            for attr_type, item_type in ITEM_TYPES.items():
                if attr_type in gene:
                    value = gene[attr_type]
                    if value is not None and value != []:
                        if isinstance(value, str):
                            items = [value.lower()]
                        else:
                            gene[attr_type] = list(set(value))
                            items = {item.lower() for item in value}
                        for item in items:
                            self._database.add_ref_record(item, concept_id, item_type,
                                                          self._src_name)
                    else:
                        del gene[attr_type]
            self._database.add_record(gene)
            self._processed_ids.append(concept_id)

    def _ftp_download(self, host: str, data_dir: str, fn: str,
                      source_dir: Path,
                      data_fn: str) -> Optional[str]:
        """Download data file from FTP site.

        :param str host: Source's FTP host name
        :param str data_dir: Data directory located on FTP site
        :param str fn: Filename for downloaded file
        :param Path source_dir: Source's data directory
        :param str data_fn: Filename on FTP site to be downloaded
        :return: Time file was last updated
        """
        with FTP(host) as ftp:
            ftp.login()
            timestamp = ftp.voidcmd(f'MDTM {data_dir}{data_fn}')[4:].strip()
            date = str(parser.parse(timestamp)).split()[0]
            version = \
                datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
            ftp.cwd(data_dir)
            self._ftp_download_file(ftp, data_fn, source_dir, fn)
        return version

    def _ftp_download_file(self, ftp: FTP, data_fn: str, source_dir: Path,
                           fn: str) -> None:
        """Download data file from FTP

        :param FTP ftp: FTP instance
        :param str data_fn: Filename on FTP site to be downloaded
        :param Path source_dir: Source's data directory
        :param str fn: Filename for downloaded file
        """
        if data_fn.endswith('.gz'):
            filepath = source_dir / f'{fn}.gz'
        else:
            filepath = source_dir / fn
        with open(filepath, 'wb') as fp:
            ftp.retrbinary(f'RETR {data_fn}', fp.write)
        if data_fn.endswith('.gz'):
            with gzip.open(filepath, 'rb') as f_in:
                with open(source_dir / fn, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            remove(filepath)

    def get_seqrepo(self, seqrepo_dir) -> SeqRepo:
        """Return SeqRepo instance if seqrepo_dir exists.

        :param Path seqrepo_dir: Path to seqrepo directory
        :return: SeqRepo instance
        """
        if not Path(seqrepo_dir).exists():
            raise NotADirectoryError(f"Could not find {seqrepo_dir}")
        return SeqRepo(seqrepo_dir)
