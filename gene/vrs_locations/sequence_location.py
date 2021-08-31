"""This module defines GA4GH Sequence Location."""
from typing import List
from ga4gh.vrs import models
from ga4gh.core import ga4gh_identify
import logging

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
        return sr.translate_alias(seqid)

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
        sequence_id = [a for a in aliases if a.startswith('ga4gh')][0]

        if gene.start != '.' and gene.end != '.' and sequence_id:
            if 0 <= gene.start <= gene.end:
                seq_location = models.SequenceLocation(
                    sequence_id=sequence_id,
                    interval=models.SequenceInterval(
                        start=models.Number(value=gene.start - 1),
                        end=models.Number(value=gene.end)
                    )
                )
                seq_location._id = ga4gh_identify(seq_location)
                location = seq_location.as_dict()
            else:
                logger.info(f"{params['concept_id']} has invalid interval:"
                            f"start={gene.start - 1} end={gene.end}")
        return location
