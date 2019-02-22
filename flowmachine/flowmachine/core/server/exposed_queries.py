from marshmallow import Schema, fields, post_load, validates, ValidationError

from ...features.subscriber import daily_location


class DailyLocationExposed:

    def __init__(self, *, date, daily_location_method, aggregation_unit, subscriber_subset):
        self.date = date
        self.daily_location_method = daily_location_method
        self.aggregation_unit = aggregation_unit
        self.subscriber_subset = subscriber_subset

        date_str = self.date.strftime("%Y-%m-%d")
        self.daily_location = daily_location(date=date_str, level=self.aggregation_unit, method=self.daily_location_method, subscriber_subset=self.subscriber_subset)

    def __repr__(self):
        return f"<DailyLocation: date='{self.date}', method='{self.daily_location_method}', aggregation_unit='{self.aggregation_unit}', subscriber_subset='{self.subscriber_subset}'>"


class DailyLocationSchema(Schema):
    date = fields.Date()
    daily_location_method = fields.String()
    aggregation_unit = fields.String()
    subscriber_subset = fields.String()

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
        allowed_values = ["all"]
        if value not in allowed_values:
            raise ValidationError(f"Subscriber subset must be one of: {allowed_values}")

    @post_load
    def make_daily_location(self, data):
        return DailyLocationExposed(**data)


schemas_of_exposed_queries = {
    "daily_location": DailyLocationSchema,
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
    return obj