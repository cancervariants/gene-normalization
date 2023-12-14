"""A base class for extraction, transformation, and loading of data."""
import logging
import re
from abc import ABC, abstractmethod
from os import environ
from pathlib import Path
from typing import Dict, List, Optional, Union

import pydantic
from biocommons.seqrepo import SeqRepo
from gffutils.feature import Feature
from wags_tails import EnsemblData, HgncData, NcbiGeneData

from gene.database import AbstractDatabase
from gene.schemas import ITEM_TYPES, Gene, GeneSequenceLocation, MatchType, SourceName

_logger = logging.getLogger(__name__)


class GeneNormalizerEtlError(Exception):
    """Basic ETL exception."""


APP_ROOT = Path(__file__).resolve().parent
SEQREPO_ROOT_DIR = Path(
    environ.get("SEQREPO_ROOT_DIR", "/usr/local/share/seqrepo/latest")
)


DATA_DISPATCH = {
    SourceName.HGNC: HgncData,
    SourceName.ENSEMBL: EnsemblData,
    SourceName.NCBI: NcbiGeneData,
}


class Base(ABC):
    """The ETL base class."""

    def __init__(
        self,
        database: AbstractDatabase,
        seqrepo_dir: Path = SEQREPO_ROOT_DIR,
        data_path: Optional[Path] = None,
        silent: bool = True,
    ) -> None:
        """Instantiate Base class.

        :param database: database instance
        :param seqrepo_dir: Path to seqrepo directory
        :param data_path: path to app data directory
        :param silent: if True, don't print ETL result to console
        """
        self._silent = silent
        self._src_name = SourceName(self.__class__.__name__)
        self._data_source = self._get_data_handler(data_path)
        self._database = database
        self.seqrepo = self.get_seqrepo(seqrepo_dir)
        self._processed_ids = list()

    def _get_data_handler(
        self, data_path: Optional[Path] = None
    ) -> Union[HgncData, EnsemblData, NcbiGeneData]:
        """Construct data handler instance for source. Overwrite for edge-case sources.

        :param data_path: location of data storage
        :return: instance of wags_tails.DataSource to manage source file(s)
        """
        return DATA_DISPATCH[self._src_name](data_dir=data_path, silent=self._silent)

    def perform_etl(self, use_existing: bool = False) -> List[str]:
        """Public-facing method to begin ETL procedures on given data.
        Returned concept IDs can be passed to Merge method for computing
        merged concepts.

        :param use_existing: if True, don't try to retrieve latest source data
        :return: list of concept IDs which were successfully processed and
            uploaded.
        """
        self._extract_data(use_existing)
        _logger.info(f"Transforming and loading {self._src_name} data to DB...")
        self._add_meta()
        self._transform_data()
        self._database.complete_write_transaction()
        _logger.info(f"Data load complete for {self._src_name}.")
        return self._processed_ids

    def _extract_data(self, use_existing: bool) -> None:
        """Acquire source data.

        This method is responsible for initializing an instance of a data handler and,
        in most cases, setting ``self._data_file`` and ``self._version``.

        :param bool use_existing: if True, don't try to fetch latest source data
        """
        _logger.info(f"Gathering {self._src_name} data...")
        self._data_file, self._version = self._data_source.get_latest(
            from_local=use_existing
        )
        _logger.info(f"Acquired data for {self._src_name}: {self._data_file}")

    @abstractmethod
    def _transform_data(self) -> None:
        """Transform data to model."""
        raise NotImplementedError

    @abstractmethod
    def _add_meta(self) -> None:
        """Add source meta to database source info."""
        raise NotImplementedError

    def _load_gene(self, gene: Dict) -> None:
        """Load a gene record into database. This method takes responsibility for:
         * validating structure correctness
         * removing duplicates from list-like fields
         * removing empty fields

        :param gene: Gene record
        """
        try:
            assert Gene(match_type=MatchType.NO_MATCH, **gene)
        except pydantic.ValidationError as e:
            _logger.warning(f"Unable to load {gene} due to validation error: " f"{e}")
        else:
            concept_id = gene["concept_id"]
            gene["label_and_type"] = f"{concept_id.lower()}##identity"
            gene["src_name"] = self._src_name.value
            gene["item_type"] = "identity"

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

        end = loc[range_ix + 1 :]
        end_arm_match = re.search("[pq]", end)

        if not end_arm_match:
            # Does not specify the arm, so use the same as start"s
            end = f"{start[0]}{end}"
            end_arm_match = re.search("[pq]", end)

        end_arm_ix = end_arm_match.start()  # type: ignore
        end_arm = end[end_arm_ix]

        if (start_arm == end_arm and start > end) or (
            start_arm != end_arm and start_arm == "p" and end_arm == "q"
        ):
            location["start"] = start
            location["end"] = end
        elif (start_arm == end_arm and start < end) or (
            start_arm != end_arm and start_arm == "q" and end_arm == "p"
        ):
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

    def _get_seq_id_aliases(self, seq_id: str) -> List[str]:
        """Get GA4GH aliases for a sequence id

        :param seq_id: Sequence ID accession
        :return: List of aliases for seqid
        """
        aliases = []
        try:
            aliases = self.seqrepo.translate_alias(seq_id, target_namespaces="ga4gh")
        except KeyError as e:
            _logger.warning(f"SeqRepo raised KeyError: {e}")
        return aliases

    def _get_sequence_location(self, seq_id: str, gene: Feature, params: Dict) -> Dict:
        """Get a gene's GeneSequenceLocation.

        :param seq_id: The sequence ID.
        :param gene: A gene from the source file.
        :param params: The transformed gene record.
        :return: A dictionary of a GA4GH VRS SequenceLocation, if seq_id alias found.
            Else, empty dictionary
        """
        location = {}
        aliases = self._get_seq_id_aliases(seq_id)
        if not aliases:
            return location

        sequence = aliases[0]

        if gene.start != "." and gene.end != "." and sequence:
            if 0 <= gene.start <= gene.end:  # type: ignore
                location = GeneSequenceLocation(
                    start=gene.start - 1,  # type: ignore
                    end=gene.end,  # type: ignore
                    sequence_id=sequence,
                ).model_dump()  # type: ignore
            else:
                _logger.warning(
                    f"{params['concept_id']} has invalid interval:"
                    f"start={gene.start - 1} end={gene.end}"
                )  # type: ignore
        return location
