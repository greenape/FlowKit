from marshmallow import Schema, fields, post_load
from marshmallow.validate import OneOf, Length

from .base import BaseExposedQuery
from ....features import TotalLocationEvents


class TotalLocationEventsExposed(BaseExposedQuery):
    def __init__(
        self,
        *,
        start_date,
        end_date,
        direction,
        interval,
        event_types,
        aggregation_unit,
        subscriber_subset,
    ):
        # TODO: disallow direction="all" in favour of direction="both"
        if direction == "all":
            direction = "both"

        # TODO: make the naming of stop/end consistent (or rather, factor this out into some DateRange or DatePeriod class)
        self.start_date = start_date
        self.end_date = end_date
        self.start_str =start_date.strftime("%Y-%m-%d")
        self.stop_str = end_date.strftime("%Y-%m-%d")
        self.direction = direction
        self.interval = interval
        self.event_types = event_types
        self.aggregation_unit = aggregation_unit
        self.subscriber_subset = subscriber_subset

        if event_types is None or event_types == []:
            tables = "all"
        else:
            tables = [f"events.{event_type}" for event_type in self.event_types]

        self.query = TotalLocationEvents(
            start=self.start_str,
            stop=self.stop_str,
            direction=direction,
            tables=tables,
            level=aggregation_unit,
            subscriber_subset=subscriber_subset,
        )

    def __repr__(self):
        return (
            f"<TotalLocationEventsExposed: start_date='{self.start_date}', end_date='{self.end_date}', direction='{self.direction}', "
            f"event_types={self.event_types}, aggregation_unit='{self.aggregation_unit}', ubscriber_subset='{self.subscriber_subset}'>"
        )


class TotalLocationEventsSchema(Schema):
    start_date = fields.Date()
    end_date = fields.Date()
    direction = fields.String(validate=OneOf(["in", "out", "both", "all"]))
    interval = fields.String(TotalLocationEvents.allowed_intervals)
    event_types = fields.List(fields.String(), allow_none=True, validate=Length(min=1))
    aggregation_unit = fields.String(validate=OneOf(["admin0", "admin1", "admin2", "admin3"]))
    subscriber_subset = fields.String(default="all", allow_none=True, validate=OneOf(["all"]))

    @post_load
    def make_query(self, params):
        return TotalLocationEventsExposed(**params)