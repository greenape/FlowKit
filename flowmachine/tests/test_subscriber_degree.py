# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Test the subscriber degree class
"""

from flowmachine.features.subscriber.subscriber_degree import (
    SubscriberDegree,
    SubscriberInDegree,
    SubscriberOutDegree,
)


def test_returns_correct_column_names(get_dataframe):
    """
    SubscriberDegree has expected column names.
    """
    assert ["subscriber", "degree"] == SubscriberDegree(
        "2016-01-01", "2016-01-04"
    ).column_names


def test_returns_correct_values(get_dataframe):
    """
    SubscriberDegree() dataframe contains expected values.
    """
    # We expect subscriber '2Dq97XmPqvL6noGk' to have a single event in df1
    # and two events in df2 (due to the larger time interval).
    ud1 = SubscriberDegree(
        "2016-01-01 12:35:00", "2016-01-01 12:40:00", table="events.sms"
    )
    ud2 = SubscriberDegree(
        "2016-01-01 12:28:00", "2016-01-01 12:40:00", table="events.sms"
    )

    df1 = get_dataframe(ud1).set_index("subscriber")
    df2 = get_dataframe(ud2).set_index("subscriber")

    assert df1.loc["2Dq97XmPqvL6noGk"]["degree"] == 1
    assert df2.loc["2Dq97XmPqvL6noGk"]["degree"] == 2


def test_returns_correct_in_out_values(get_dataframe):
    """
    SubscriberIn/OutDegree() dataframe contains expected values.
    """
    # We expect subscriber '2Dq97XmPqvL6noGk' to not appear in df1, because they
    # only received a text, and to have degree 1 in in df2 because they
    # also sent one.
    ud1 = SubscriberInDegree(
        "2016-01-01 12:35:00", "2016-01-01 12:40:00", table="events.sms"
    )
    ud2 = SubscriberOutDegree(
        "2016-01-01 12:28:00", "2016-01-01 12:40:00", table="events.sms"
    )

    df1 = get_dataframe(ud1)
    df2 = get_dataframe(ud2).set_index("subscriber")

    assert "2Dq97XmPqvL6noGk" not in df1.subscriber.values
    assert df2.loc["2Dq97XmPqvL6noGk"]["degree"] == 1
