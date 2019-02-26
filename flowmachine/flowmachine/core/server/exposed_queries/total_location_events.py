from marshmallow import Schema, fields, validates, ValidationError, post_load
from marshmallow.validate import OneOf

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

        self.query = TotalLocationEvents(
            start=self.start_str,
            stop=self.stop_str,
            direction=direction,
            table=event_types,
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
    event_types = fields.String()  # TODO: can also be a list of strings!
    aggregation_unit = fields.String(validate=OneOf(["admin0", "admin1", "admin2", "admin3"]))
    subscriber_subset = fields.String(default="all", allow_none=True, validate=OneOf(["all"]))

    @validates("direction")
    def validate_direction(self, value):
        allowed_values = ["in", "out", "both", "all"]
        if value not in allowed_values:
            raise ValidationError(f"Direction must be one of: {allowed_values}")

    @post_load
    def make_query(self, params):
        return TotalLocationEventsExposed(**params)