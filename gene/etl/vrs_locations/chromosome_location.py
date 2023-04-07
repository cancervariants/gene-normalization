"""This module defines GA4GH Chromosome Location."""
import re
import logging
from typing import Dict, Optional

from pydantic.error_wrappers import ValidationError

from gene.schemas import GeneChromosomeLocation


logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class ChromosomeLocation:
    """The class for GA4GH Chromosome Location."""

    def get_location(self, location: Dict, gene: Dict) -> Optional[Dict]:
        """Transform a gene's location into a Chromosome Location.

        :param location: A gene's location.
        :param gene: A transformed gene record.
        :return: If location is a valid VRS ChromosomeLocation, return a dictionary
            containing the ChromosomeLocation. Else, return None.
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
                chr_location = GeneChromosomeLocation(
                    chr=location["chr"],
                    start=location["start"],
                    end=location["end"]).dict()
            except ValidationError as e:
                logger.info(f"{e} for {gene['symbol']}")
            else:
                return chr_location
        return None

    def set_interval_range(self, loc: str, arm_ix: int, location: Dict) -> None:
        """Set the location interval range.

        :param loc: A gene location
        :param arm_ix: The index of the q or p arm for a given location
        :param location: A gene's location
        """
        range_ix = re.search('-', loc).start()  # type: ignore

        start = loc[arm_ix:range_ix]
        start_arm_ix = re.search("[pq]", start).start()  # type: ignore
        start_arm = start[start_arm_ix]

        end = loc[range_ix + 1:]
        end_arm_match = re.search("[pq]", end)

        if not end_arm_match:
            # Does not specify the arm, so use the same as start's
            end = f"{start[0]}{end}"
            end_arm_match = re.search("[pq]", end)

        end_arm_ix = end_arm_match.start()  # type: ignore
        end_arm = end[end_arm_ix]

        if (start_arm == end_arm and start > end) or \
                (start_arm != end_arm and start_arm == 'p' and end_arm == 'q'):
            location['start'] = start
            location['end'] = end
        elif (start_arm == end_arm and start < end) or \
                (start_arm != end_arm and start_arm == 'q' and end_arm == 'p'):
            location['start'] = end
            location['end'] = start
