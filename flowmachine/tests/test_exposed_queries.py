from flowmachine.core.server.exposed_queries import make_query_object, DailyLocationExposed


def test_daily_location():

    dl_params = {
        'date': '2016-01-01',
        'method': 'most-common',
        'aggregation_unit': 'admin3',
        'subscriber_subset': 'all',
    }

    dl = make_query_object("daily_location", dl_params)

    assert isinstance(dl, DailyLocationExposed)
    assert "2016-01-01" == dl.date.strftime("%Y-%m-%d")
    assert "most-common" == dl.method
    assert "admin3" == dl.aggregation_unit
    assert "all" == dl.subscriber_subset
