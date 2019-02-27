import pytest

from flowmachine.core.server.exposed_queries.exposed_queries import (
    make_query_object,
    QueryParamsValidationError,
)
from flowmachine.core.server.exposed_queries import *


def test_daily_location():
    """
    Can successfully construct a daily location object from valid parameters.
    """

    dl_params = {
        "date": "2016-01-01",
        "daily_location_method": "most-common",
        "aggregation_unit": "admin3",
        "subscriber_subset": "all",
    }

    dl = make_query_object("daily_location", dl_params)

    assert isinstance(dl, DailyLocationExposed)
    assert "2016-01-01" == dl.date.strftime("%Y-%m-%d")
    assert "most-common" == dl.daily_location_method
    assert "admin3" == dl.aggregation_unit
    assert "all" == dl.subscriber_subset


@pytest.mark.parametrize(
    "param_name, invalid_value, expected_error_msg",
    [
        ("date", "3999-99-99", "Not a valid date"),
        (
            "daily_location_method",
            "foobar",
            "{'daily_location_method': \['Not a valid choice.'\]}",
        ),
        (
            "aggregation_unit",
            "admin99",
            "{'aggregation_unit': \['Not a valid choice.'\]}",
        ),
        (
            "subscriber_subset",
            "<INVALID_SUBSCRIBER>",
            "{'subscriber_subset': \['Not a valid choice.'\]}",
        ),
    ],
)
def test_invalid_date_raises_error(param_name, invalid_value, expected_error_msg):
    # Start with valid parameters
    params = {
        "date": "2016-01-01",
        "daily_location_method": "most-common",
        "aggregation_unit": "admin3",
        "subscriber_subset": "all",
    }

    # Replace one of the parameters with an invalid valie
    params[param_name] = invalid_value

    # Confirm that the invalid parameter causes the expected error
    with pytest.raises(QueryParamsValidationError, match=expected_error_msg):
        make_query_object("daily_location", params)


def test_location_event_counts():
    """
    Can successfully construct a total location events object from valid parameters.
    """

    params = {
        "start_date": "2016-01-01",
        "end_date": "2016-01-04",
        "direction": "out",
        "interval": "hour",
        "event_types": None,
        "aggregation_unit": "admin3",
        "subscriber_subset": "all",
    }

    q = make_query_object("location_event_counts", params)

    assert isinstance(q, LocationEventCountsExposed)
    assert "2016-01-01" == q.start_date.strftime("%Y-%m-%d")
    assert "2016-01-04" == q.end_date.strftime("%Y-%m-%d")
    assert "out" == q.direction
    assert "hour" == q.interval
    assert None == q.event_types
    assert "admin3" == q.aggregation_unit
    assert "all" == q.subscriber_subset


def test_subscriber_locations():
    """
    Can successfully construct a total location events object from valid parameters.
    """

    params = {"start": "2016-01-01", "stop": "2016-01-04"}

    q = make_query_object("subscriber_locations", params)

    assert isinstance(q, SubscriberLocationsExposed)
    assert "2016-01-01" == q.start_date.strftime("%Y-%m-%d")
    assert "2016-01-04" == q.stop_date.strftime("%Y-%m-%d")
