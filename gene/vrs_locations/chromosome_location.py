"""This module defines GA4GH Chromosome Location."""
from ga4gh.vrs import models
from ga4gh.core import ga4gh_identify
import re
import logging

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class ChromosomeLocation:
    """The class for GA4GH Chromosome Location."""

    def add_location(self, location, interval):
        """Get a gene's Chromosome Location.

        :param dict location: A gene's location.
        :param dict interval: A gene's start and end location.
        :return: A dictionary of a GA4GH VRS ChromosomeLocation.
        """
        chr_location = models.ChromosomeLocation(
            species_id="taxonomy:9606",
            chr=location['chr'],
            interval=models.CytobandInterval(
                start=interval['start'],
                end=interval['end']
            )
        )
        chr_location._id = ga4gh_identify(chr_location)
        return chr_location.as_dict()

    def set_interval_range(self, loc, arm_ix, interval):
        """Set the location interval range.

        :param str loc: A gene location
        :param int arm_ix: The index of the q or p arm for a given location
        :param dict interval: The GA4GH interval for a VRS object
        """
        range_ix = re.search('-', loc).start()

        start = loc[arm_ix:range_ix]
        start_arm_ix = re.search("[pq]", start).start()
        start_arm = start[start_arm_ix]

        end = loc[range_ix + 1:]
        end_arm_match = re.search("[pq]", end)

        if not end_arm_match:
            # Does not specify the arm, so use the same as start's
            end = f"{start[0]}{end}"
            end_arm_match = re.search("[pq]", end)

        end_arm_ix = end_arm_match.start()
        end_arm = end[end_arm_ix]

        if (start_arm == end_arm and start > end) or \
                (start_arm != end_arm and start_arm == 'p' and end_arm == 'q'):
            interval['start'] = start
            interval['end'] = end
        elif (start_arm == end_arm and start < end) or \
                (start_arm != end_arm and start_arm == 'q' and end_arm == 'p'):
            interval['start'] = end
            interval['end'] = start
