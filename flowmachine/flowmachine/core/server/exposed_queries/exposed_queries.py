import logging
import marshmallow

from .daily_location import DailyLocationSchema
from .location_event_counts import LocationEventCountsSchema

logger = logging.getLogger("flowmachine").getChild(__name__)


schemas_of_exposed_queries = {
    "daily_location": DailyLocationSchema,
    "location_event_counts": LocationEventCountsSchema,
}


class InvalidQueryKind(Exception):
    """
    Custom exception to indicate an unsupported query kind.
    """


class QueryParamsValidationError(Exception):
    """
    Custom exception to indicate an error during validation of query parameters.
    """

    def __init__(self, messages):
        super().__init__(messages)
        self.messages = messages


def make_query_object(query_kind, params):
    try:
        schema_cls = schemas_of_exposed_queries[query_kind]
    except KeyError:
        raise InvalidQueryKind()

    try:
        obj = schema_cls().load(params)
    except marshmallow.ValidationError as exc:
        # We raise our own custom exception here so that any callers do not
        # need to know about our internal use of marshmallow for validation.
        raise QueryParamsValidationError(exc.messages)

    logger.debug(f"Made query of kind '{query_kind}' with parameters: {params}")
    return obj
