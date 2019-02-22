import logging
from marshmallow import Schema, fields, post_load, validates, ValidationError

from ...features import daily_location, TotalLocationEvents

logger = logging.getLogger("flowmachine").getChild(__name__)


class AggregationError(Exception):
    """
    Custom exception to indicate that a query does not support aggregation.
    """


class BaseExposedQuery:

    def store(self, force=False):
        self.query.store(force=force)

    def aggregate(self):
        try:
            return self.query.aggregate()
        except AttributeError:
            raise AggregationError(f"Query does not support aggregation: {type(self.query)}")

    @property
    def md5(self):
        return self.query.md5


class DailyLocationExposed(BaseExposedQuery):

    def __init__(self, *, date, daily_location_method, aggregation_unit, subscriber_subset):
        self.date = date
        self.daily_location_method = daily_location_method
        self.aggregation_unit = aggregation_unit
        self.subscriber_subset = subscriber_subset

        date_str = self.date.strftime("%Y-%m-%d")
        self.query = daily_location(date=date_str, level=self.aggregation_unit, method=self.daily_location_method, subscriber_subset=self.subscriber_subset)

    def __repr__(self):
        return f"<DailyLocation: date='{self.date}', method='{self.daily_location_method}', aggregation_unit='{self.aggregation_unit}', subscriber_subset='{self.subscriber_subset}'>"


class DailyLocationSchema(Schema):
    date = fields.Date()
    daily_location_method = fields.String()
    aggregation_unit = fields.String()
    subscriber_subset = fields.String(default="all", allow_none=True)

    @validates("daily_location_method")
    def validate_daily_location_method(self, value):
        allowed_values = ["last", "most-common"]
        if value not in allowed_values:
            raise ValidationError(f"Method must be one of: {allowed_values}")

    @validates("aggregation_unit")
    def validate_aggregation_unit(self, value):
        allowed_values = ["admin0", "admin1", "admin2", "admin3"]
        if value not in allowed_values:
            raise ValidationError(f"Aggregation unit must be one of: {allowed_values}")

    @validates("subscriber_subset")
    def validate_subscriber_subset(self, value):
        allowed_values = [None, "all"]
        if value not in allowed_values:
            raise ValidationError(f"Subscriber subset must be one of: {allowed_values}")

    @post_load
    def make_daily_location(self, params):
        return DailyLocationExposed(**params)


class TotalLocationEventsExposed(BaseExposedQuery):

    def __init__(self, *, start_date, end_date, direction, interval, event_types, aggregation_unit, subscriber_subset):
        self.start_str = start_date.strftime("%Y-%m-%d")
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
            f"<TotalLocationEvents: start_date='{self.start_date}', end_date='{self.end_date}', direction='{self.direction}', "
            f"event_types={self.event_types}, aggregation_unit='{self.aggregation_unit}', ubscriber_subset='{self.subscriber_subset}'>"
        )


class TotalLocationEventsSchema(Schema):
    start_date = fields.Date()
    end_date = fields.Date()
    direction = fields.String()
    interval = fields.String()
    event_types = fields.String()  # TODO: can also be a list of strings!
    aggregation_unit = fields.String()
    subscriber_subset = fields.String(default="all", allow_none=True)

    @validates("direction")
    def validate_direction(self, value):
        allowed_values = ["in", "out", "both"]
        if value not in allowed_values:
            raise ValidationError(f"Direction must be one of: {allowed_values}")

    @post_load
    def make_query(self, params):
        return TotalLocationEventsExposed(**params)


schemas_of_exposed_queries = {
    "daily_location": DailyLocationSchema,
    "location_event_counts": TotalLocationEventsSchema,
}


class InvalidQueryKind(Exception):
    """
    Custom exception to indicate an unsupported query kind.
    """

def make_query_object(query_kind, params):
    try:
        schema_cls = schemas_of_exposed_queries[query_kind]
    except KeyError:
        raise InvalidQueryKind()

    obj = schema_cls().load(params)
    logger.debug(f"Made query of kind '{query_kind}' with parameters: {params}")
    return obj