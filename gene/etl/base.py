"""A base class for extraction, transformation, and loading of data."""
import re
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from pathlib import Path
from ftplib import FTP
import gzip
import shutil
from os import remove
from dateutil import parser
import datetime
import logging

from gffutils.feature import Feature
from biocommons.seqrepo import SeqRepo
import pydantic

from gene.database import AbstractDatabase
from gene import ITEM_TYPES, SEQREPO_ROOT_DIR
from gene.schemas import Gene, MatchType, SourceName, GeneSequenceLocation

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class Base(ABC):
    """The ETL base class."""

    def __init__(self, database: AbstractDatabase, host: str, data_dir: str,
                 src_data_dir: Path, seqrepo_dir: Path = SEQREPO_ROOT_DIR,
                 *args, **kwargs) -> None:
        """Instantiate Base class.

        :param database: database instance
        :param host: Hostname of FTP site
        :param data_dir: Data directory of FTP site to look at
        :param src_data_dir: Data directory for source
        :param seqrepo_dir: Path to seqrepo directory
        """
        self._src_name = SourceName(self.__class__.__name__)
        self._database = database
        self._host = host
        self._data_dir = data_dir
        self.src_data_dir = src_data_dir
        self._processed_ids = list()
        self.seqrepo = self.get_seqrepo(seqrepo_dir)

    @abstractmethod
    def perform_etl(self) -> List[str]:
        """Extract, Transform, and Load data into database.

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
        """Add source meta to database source info."""
        raise NotImplementedError

    def _create_data_directory(self) -> None:
        """Create data directory for source."""
        self.src_data_dir.mkdir(exist_ok=True, parents=True)

    def _load_gene(self, gene: Dict) -> None:
        """Load a gene record into database. This method takes responsibility for:
         * validating structure correctness
         * removing duplicates from list-like fields
         * removing empty fields

        :param gene: Gene record
        """
        try:
            assert Gene(match_type=MatchType.NO_MATCH, **gene)
        except pydantic.error_wrappers.ValidationError as e:
            logger.warning(f"Unable to load {gene} due to validation error: "
                           f"{e}")
        else:
            concept_id = gene['concept_id']
            gene['label_and_type'] = f"{concept_id.lower()}##identity"
            gene["src_name"] = self._src_name.value
            gene['item_type'] = 'identity'

            for attr_type in ITEM_TYPES:
                if attr_type in gene:
                    value = gene[attr_type]
                    if value is None or value == []:
                        del gene[attr_type]
                    elif isinstance(value, str):
                        continue
                    gene[attr_type] = list(set(value))

            self._database.add_record(gene, self._src_name)
            self._processed_ids.append(concept_id)

    def _ftp_download(self, host: str, data_dir: str, fn: str, source_dir: Path,
                      data_fn: str) -> Optional[str]:
        """Download data file from FTP site.

        :param host: Source's FTP host name
        :param data_dir: Data directory located on FTP site
        :param fn: Filename for downloaded file
        :param source_dir: Source's data directory
        :param data_fn: Filename on FTP site to be downloaded
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

        :param ftp: FTP instance
        :param data_fn: Filename on FTP site to be downloaded
        :param source_dir: Source's data directory
        :param fn: Filename for downloaded file
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

    def get_seqrepo(self, seqrepo_dir: Path) -> SeqRepo:
        """Return SeqRepo instance if seqrepo_dir exists.

        :param seqrepo_dir: Path to seqrepo directory
        :return: SeqRepo instance
        """
        if not Path(seqrepo_dir).exists():
            raise NotADirectoryError(f"Could not find {seqrepo_dir}")
        return SeqRepo(seqrepo_dir)

    def _set_cl_interval_range(self, loc: str, arm_ix: int, location: Dict) -> None:
        """Set the Chromosome location interval range.

        :param loc: A gene location
        :param arm_ix: The index of the q or p arm for a given location
        :param location: VRS chromosome location. This will be mutated.
        """
        range_ix = re.search("-", loc).start()  # type: ignore

        start = loc[arm_ix:range_ix]
        start_arm_ix = re.search("[pq]", start).start()  # type: ignore
        start_arm = start[start_arm_ix]

        end = loc[range_ix + 1:]
        end_arm_match = re.search("[pq]", end)

        if not end_arm_match:
            # Does not specify the arm, so use the same as start"s
            end = f"{start[0]}{end}"
            end_arm_match = re.search("[pq]", end)

        end_arm_ix = end_arm_match.start()  # type: ignore
        end_arm = end[end_arm_ix]

        if (start_arm == end_arm and start > end) or \
                (start_arm != end_arm and start_arm == "p" and end_arm == "q"):
            location["start"] = start
            location["end"] = end
        elif (start_arm == end_arm and start < end) or \
                (start_arm != end_arm and start_arm == "q" and end_arm == "p"):
            location["start"] = end
            location["end"] = start

    # Add back once VRS Chromosome Location is supported in 2.0-alpha
    # def _get_chromosome_location(self, location: Dict, gene: Dict) -> Optional[Dict]:
    #     """Transform a gene's location into a GeneChromosomeLocation.

    #     :param location: A gene's location.
    #     :param gene: A transformed gene record.
    #     :return: If location is a valid VRS ChromosomeLocation, return a dictionary
    #         containing the ChromosomeLocation. Else, return None.
    #     """
    #     if "chr" in location and "start" in location and "end" in location:
    #         if location["start"] == "p" and location["end"] == "p":
    #             location["start"] = "pter"
    #             location["end"] = "cen"
    #         elif location["start"] == "q" and location["end"] == "q":
    #             location["start"] = "cen"
    #             location["end"] = "qter"
    #         try:
    #             chr_location = GeneChromosomeLocation(
    #                 chr=location["chr"],
    #                 start=location["start"],
    #                 end=location["end"]).model_dump()
    #         except ValidationError as e:
    #             logger.info(f"{e} for {gene['symbol']}")
    #         else:
    #             return chr_location
    #     return None

    def _get_seq_id_aliases(self, sr: SeqRepo, seq_id: str) -> List[str]:
        """Get GA4GH aliases for a sequence id

        :param sr: seqrepo instance
        :param seq_id: Sequence ID accession
        :return: List of aliases for seqid
        """
        aliases = []
        try:
            aliases = sr.translate_alias(seq_id, target_namespaces="ga4gh")
        except KeyError as e:
            logger.warning(f"SeqRepo raised KeyError: {e}")
        return aliases

    def _get_sequence_location(
        self, seq_id: str, gene: Feature, params: Dict, sr: SeqRepo
    ) -> Dict:
        """Get a gene's GeneSequenceLocation.

        :param seq_id: The sequence ID.
        :param gene: A gene from the source file.
        :param params: The transformed gene record.
        :param sr: Access to the SeqRepo
        :return: A dictionary of a GA4GH VRS SequenceLocation, if seq_id alias found.
            Else, empty dictionary
        """
        location = {}
        aliases = self._get_seq_id_aliases(sr, seq_id)
        if not aliases:
            return location

        sequence = aliases[0]

        if gene.start != "." and gene.end != "." and sequence:
            if 0 <= gene.start <= gene.end:  # type: ignore
                location = GeneSequenceLocation(
                    start=gene.start - 1,  # type: ignore
                    end=gene.end,  # type: ignore
                    sequence_id=sequence
                ).model_dump()  # type: ignore
            else:
                logger.info(f"{params['concept_id']} has invalid interval:"
                            f"start={gene.start - 1} end={gene.end}")  # type: ignore
        return location
