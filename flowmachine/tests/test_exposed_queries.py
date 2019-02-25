import pytest

from flowmachine.core.server.exposed_queries.exposed_queries import (
    make_query_object,
    QueryParamsValidationError,
)
from flowmachine.core.server.exposed_queries.daily_location import DailyLocationExposed


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
        ("daily_location_method", "foobar", "Method must be one of"),
        ("aggregation_unit", "admin99", "Aggregation unit must be one of"),
        (
            "subscriber_subset",
            "<INVALID_SUBSCRIBER>",
            "Subscriber subset must be one of",
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

    # Confirm that the invalid parameter causes the expeted error
    with pytest.raises(QueryParamsValidationError, match=expected_error_msg):
        make_query_object("daily_location", params)
