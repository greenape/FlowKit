# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Classes that deal with finding a list of locations for subscribers.
Note these classes return multiple locations for each subscriber,
and therefore do not represent a single home location for each
subscribers. Mostly they are not used directly, but are called by
dailylocations objects, although they can be.

"""

import logging

from flowmachine.utils import parse_datestring, get_columns_for_level

from ...core import CustomQuery

logger = logging.getLogger("flowmachine").getChild(__name__)


class MultiLocation:
    """
    Abstract base class for any class that involves stitching together
    multiple daily locations (or similar).

    The class object takes a start and stop datetime, and optionally
    a list of daily locations objects and returns a day-dated list of locations of
    each subscriber. This will be the first location in the event of a tie.
    Subscribers are guaranteed to have a Day Trajectory if they appear in any of
    the daily_locs objects.

    Parameters
    ----------
    daily_locations : list, optional list of flowmachine.daily_location objects
            to use for calculation.
    """

    def __init__(self, *daily_locations):
        # TODO: check that all the inputs are actually location objects (of an appropriate kind)

        self.start = str(
            min(
                parse_datestring(daily_location.start)
                for daily_location in daily_locations
            )
        )
        self.stop = str(
            max(
                parse_datestring(daily_location.start)
                for daily_location in daily_locations
            )
        )
        self._all_dls = daily_locations
        logger.info("ModalLocation using {} DailyLocations".format(len(self._all_dls)))
        logger.info(
            "{}/{} DailyLocations are pre-calculated.".format(
                sum(1 for dl in self._all_dls if dl.is_stored), len(self._all_dls)
            )
        )

        # Importing daily_location inputs
        # from first daily_location object.
        self.level = self._all_dls[0].level
        self.subscriber_identifier = self._all_dls[0].subscriber_identifier
        self.column_name = self._all_dls[0].column_name
        super().__init__()

    def _append_date(self, dl):
        """
        Takes a daily location object and returns a query representing that
        daily location, but with an additional (constant) column with the
        date to which that daily-loc applies.

        Returns
        -------
        CustomQuery
        """

        date_string = f"to_date('{dl.start}','YYYY-MM-DD') AS date"
        sql = f"SELECT *, {date_string} FROM ({dl.get_query()}) AS dl"
        return CustomQuery(
            sql, get_columns_for_level(self.level, self.column_name) + ["date"]
        )

    def _get_relevant_columns(self):
        """
        Get a string of the location related columns
        """

        return ", ".join(get_columns_for_level(self.level, self.column_name))
