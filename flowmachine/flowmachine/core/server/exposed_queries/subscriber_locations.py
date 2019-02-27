from marshmallow import Schema, fields, post_load

from .base import BaseExposedQuery
from ....features import subscriber_locations

__all__ = ["SubscriberLocationsExposed", "SubscriberLocationsSchema"]


class SubscriberLocationsExposed(BaseExposedQuery):
    def __init__(self, *, start, stop):
        self.start_date = start
        self.stop_date = stop

        start_date_str = self.start_date.strftime("%Y-%m-%d")
        stop_date_str = self.stop_date.strftime("%Y-%m-%d")
        self.query = subscriber_locations(start=start_date_str, stop=stop_date_str)

    def __repr__(self):
        return f"<{self.__class__.__name__}: start_date='{self.start_date}', stop_date='{self.stop_date}'>"


class SubscriberLocationsSchema(Schema):
    start = fields.Date()
    stop = fields.Date()

    @post_load
    def make_query_object(self, params):
        return SubscriberLocationsExposed(**params)
