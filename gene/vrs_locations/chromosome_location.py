"""This module defines GA4GH Chromosome Location."""
from ga4gh.vrs import models
from ga4gh.core import ga4gh_identify
from gene.schemas import ChromosomeLocation as vrs_cl
import re
import logging
import python_jsonschema_objects

logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class ChromosomeLocation:
    """The class for GA4GH Chromosome Location."""

    def add_location(self, location):
        """Get a gene's Chromosome Location.

        :param dict location: A gene's location.
        :return: A dictionary of a GA4GH VRS ChromosomeLocation.
        """
        chr_location = models.ChromosomeLocation(
            species_id="taxonomy:9606",
            chr=location['chr'],
            interval=models.CytobandInterval(
                start=location['start'],
                end=location['end']
            )
        )
        chr_location._id = ga4gh_identify(chr_location)
        return chr_location.as_dict()

    def get_location(self, location, gene):
        """Transform a gene's location into a Chromosome Location.

        :param dict location: A gene's location.
        :param dict gene: A transformed gene record.
        :return: If location is a valid VRS ChromosomeLocation, return a
         dictionary containing the ChromosomeLocation.
         Else, return None.
        """
        if 'chr' in location and 'start' in location \
                and 'end' in location:
            if location['start'] == 'p' and location['end'] == 'p':
                location['start'] = 'pter'
                location['end'] = 'cen'
            elif location['start'] == 'q' and \
                    location['end'] == 'q':
                location['start'] = 'cen'
                location['end'] = 'qter'
            try:
                chr_location = \
                    self.add_location(
                        location)
                assert vrs_cl(**chr_location)
            except python_jsonschema_objects.validators. \
                    ValidationError as e:
                logger.info(f"{e} for {gene['symbol']}")
            else:
                return chr_location
        return None

    def set_interval_range(self, loc, arm_ix, location):
        """Set the location interval range.

        :param str loc: A gene location
        :param int arm_ix: The index of the q or p arm for a given location
        :param dict location: A gene's location
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
            location['start'] = start
            location['end'] = end
        elif (start_arm == end_arm and start < end) or \
                (start_arm != end_arm and start_arm == 'q' and end_arm == 'p'):
            location['start'] = end
            location['end'] = start
