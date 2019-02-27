from marshmallow import Schema, fields, post_load
from marshmallow.validate import OneOf

from .base import BaseExposedQuery
from ....features import daily_location


class DailyLocationExposed(BaseExposedQuery):
    def __init__(
        self, *, date, daily_location_method, aggregation_unit, subscriber_subset
    ):
        self.date = date
        self.daily_location_method = daily_location_method
        self.aggregation_unit = aggregation_unit
        self.subscriber_subset = subscriber_subset

        date_str = self.date.strftime("%Y-%m-%d")
        self.query = daily_location(
            date=date_str,
            level=self.aggregation_unit,
            method=self.daily_location_method,
            subscriber_subset=self.subscriber_subset,
        )

    def __repr__(self):
        return f"<DailyLocationExposed: date='{self.date}', method='{self.daily_location_method}', aggregation_unit='{self.aggregation_unit}', subscriber_subset='{self.subscriber_subset}'>"


class DailyLocationSchema(Schema):
    date = fields.Date()
    daily_location_method = fields.String(validate=OneOf(["last", "most-common"]))
    aggregation_unit = fields.String(
        validate=OneOf(["admin0", "admin1", "admin2", "admin3"])
    )
    subscriber_subset = fields.String(
        default="all", allow_none=True, validate=OneOf(["all"])
    )

    @post_load
    def make_query_object(self, params):
        return DailyLocationExposed(**params)
