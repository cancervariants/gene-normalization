"""This module defines GA4GH Sequence Location."""
from typing import List
import logging

from gene.schemas import GeneSequenceLocation

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class SequenceLocation:
    """The class for GA4GH Sequence Location."""

    def get_aliases(self, sr, seqid) -> List[str]:
        """Get aliases for a sequence id

        :param SeqRepo sr: seqrepo instance
        :param str seqid: Sequence ID accession
        :return: List of aliases for seqid
        """
        aliases = []
        try:
            aliases = sr.translate_alias(seqid)
        except KeyError as e:
            logger.warning(f"SeqRepo raised KeyError: {e}")
        return aliases

    def add_location(self, seqid, gene, params, sr):
        """Get a gene's Sequence Location.

        :param str seqid: The sequence ID.
        :param Feature gene: A gene from the source file.
        :param dict params: The transformed gene record.
        :param SeqRepo sr: Access to the SeqRepo
        :return: A dictionary of a GA4GH VRS SequenceLocation.
        """
        location = dict()
        aliases = self.get_aliases(sr, seqid)
        if not aliases:
            return location

        sequence_id = [a for a in aliases if a.startswith('ga4gh')][0]

        if gene.start != '.' and gene.end != '.' and sequence_id:
            if 0 <= gene.start <= gene.end:
                location = GeneSequenceLocation(
                    start=gene.start - 1,
                    end=gene.end,
                    sequence_id=sequence_id).dict()
            else:
                logger.info(f"{params['concept_id']} has invalid interval:"
                            f"start={gene.start - 1} end={gene.end}")
        return location
