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
            raise AggregationError(
                f"Query does not support aggregation: {type(self.query)}"
            )

    @property
    def md5(self):
        return self.query.md5
