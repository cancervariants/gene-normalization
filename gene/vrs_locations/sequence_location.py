"""This module defines GA4GH Sequence Location."""
from ga4gh.vrs import models
from ga4gh.core import ga4gh_identify
import logging
from gene.schemas import SequenceLocation as vrs_sl

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class SequenceLocation:
    """The class for GA4GH Sequence Location."""

    def add_location(self, seqid, gene, params, sr):
        """Get a gene's Sequence Location.

        :param str seqid: The sequence ID.
        :param Feature gene: A gene from the source file.
        :param dict params: The transformed gene record.
        :param SeqRepo sr: Access to the SeqRepo
        :return: A dictionary of a GA4GH VRS SequenceLocation.
        """
        location = dict()
        aliases = sr.translate_alias(seqid)
        sequence_id = [a for a in aliases if a.startswith('ga4gh')][0]

        if gene.start != '.' and gene.end != '.' and sequence_id:
            if 0 <= gene.start <= gene.end:
                seq_location = models.SequenceLocation(
                    sequence_id=sequence_id,
                    interval=models.SimpleInterval(
                        start=gene.start,
                        end=gene.end
                    )
                )
                seq_location._id = ga4gh_identify(seq_location)
                location = seq_location.as_dict()
                assert vrs_sl(**location)
            else:
                logger.info(f"{params['concept_id']} has invalid interval:"
                            f"start={gene.start} end={gene.end}")
        return location
