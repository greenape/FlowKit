# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# -*- coding: utf-8 -*-

"""
Functions which deal with inspecting cached tables.
"""
import logging
import pickle

from typing import TYPE_CHECKING, Tuple, List

from psycopg2 import InternalError

if TYPE_CHECKING:
    from .query import Query
    from .connection import Connection

logger = logging.getLogger("flowmachine").getChild(__name__)


def touch_cache(connection: "Connection", query_id: str) -> float:
    """
    'Touch' a cache record and update the cache score for it.

    Parameters
    ----------
    connection : Connection
    query_id : str
        md5 id of the query to touch

    Returns
    -------
    float
        The new cache score
    """
    try:
        return float(connection.fetch(f"SELECT touch_cache('{query_id}')")[0][0])
    except (IndexError, InternalError):
        raise ValueError(f"Query id '{query_id}' is not in cache on this connection.")


def reset_cache(connection: "Connection") -> None:
    """
    Reset the query cache. Deletes any tables under cache schema, resets the cache count
    and clears the cached and dependencies tables.

    Parameters
    ----------
    connection : Connection
    """
    qry = f"SELECT tablename FROM cache.cached WHERE NOT class='Table'"
    tables = connection.fetch(qry)
    with connection.engine.begin() as trans:
        trans.execute("SELECT setval('cache.cache_touches', 1)")
        for table in tables:
            trans.execute(f"DROP TABLE IF EXISTS cache.{table[0]} CASCADE")
        trans.execute("TRUNCATE cache.cached CASCADE")
        trans.execute("TRUNCATE cache.dependencies CASCADE")


def get_query_by_id(connection: "Connection", query_id: str) -> "Query":
    """
    Get a query object from cache by id.

    Parameters
    ----------
    connection : Connection
    query_id : str
        md5 id of the query

    Returns
    -------
    Query
        The original query object.

    """
    qry = f"SELECT obj FROM cache.cached WHERE query_id='{query_id}'"
    try:
        obj = connection.fetch(qry)[0][0]
        return pickle.loads(obj)
    except IndexError:
        raise ValueError(f"Query id '{query_id}' is not in cache on this connection.")


def get_cached_queries_by_score(connection: "Connection") -> List[Tuple["Query", int]]:
    """
    Get all cached queries in ascending cache score order.

    Parameters
    ----------
    connection : Connection

    Returns
    -------
    list of tuples
        Returns a list of cached Query objects with their on disk sizes

    """
    qry = """SELECT obj, table_size(tablename, schema) as table_size
        FROM cache.cached
        WHERE NOT cached.class='Table'
        ORDER BY cache_score_multiplier*((compute_time/1000)/table_size(tablename, schema)) ASC
        """
    cache_queries = connection.fetch(qry)
    return [(pickle.loads(obj), table_size) for obj, table_size in cache_queries]


def shrink_one(connection: "Connection", dry_run: bool = False) -> "Query":
    """
    Remove the lowest scoring cached query from cache and return it and size of it
    in bytes.

    Parameters
    ----------
    connection : "Connection"
    dry_run : bool, default False
        Set to true to just report the object that would be removed and not remove it

    Returns
    -------
    tuple of "Query", int
        The "Query" object that was removed from cache and the size of it
    """
    obj_to_remove, obj_size = get_cached_queries_by_score(connection)[0]

    logger.info(
        f"{'Would' if dry_run else 'Will'} remove cache record for {obj_to_remove.md5} of type {obj_to_remove.__class__}"
    )
    logger.info(
        f"Table {obj_to_remove.table_name} ({obj_size} bytes) {'would' if dry_run else 'will'} be removed."
    )

    if not dry_run:
        obj_to_remove.invalidate_db_cache(cascade=False, drop=True)
    return obj_to_remove, obj_size


def shrink_below_size(
    connection: "Connection", size_threshold: int = None, dry_run: bool = False
) -> "Query":
    """
    Remove queries from the cache until it is below a specified size threshold.

    Parameters
    ----------
    connection : "Connection"
    size_threshold : int, default None
        Optionally override the maximum cache size set in flowdb.
    dry_run : bool, default False
        Set to true to just report the objects that would be removed and not remove them

    Returns
    -------
    list of "Query"
        List of the queries that were removed
    """
    initial_cache_size = size_of_cache(connection)
    removed = []
    logger.info(
        f"Shrinking cache from {initial_cache_size} to below {size_threshold}{'(dry run)' if dry_run else ''}."
    )

    if dry_run:
        cached_queries = iter(get_cached_queries_by_score(connection))
        shrink = lambda x: cached_queries.__next__()
    else:
        shrink = shrink_one

    while initial_cache_size > size_threshold:
        obj_removed, cache_reduction = shrink(connection)
        removed.append(obj_removed)
        initial_cache_size -= cache_reduction
    logger.info(
        f"New cache size {'would' if dry_run else 'will'} be {initial_cache_size}."
    )
    return removed


def size_of_table(connection: "Connection", table_name: str, table_schema: str) -> int:
    """
    Get the size on disk in bytes of a table in the database.

    Parameters
    ----------
    connection : "Connection"
    table_name : str
        Name of table to get size of
    table_schema : str
        Schema of the table

    Returns
    -------
    int
        Number of bytes on disk this table uses in total

    """
    sql = f"SELECT table_size('{table_name}', '{table_schema}')"
    try:
        return int(connection.fetch(sql)[0][0])
    except IndexError:
        raise ValueError(
            f"Table '{table_schema}.{table_name}' does not exist on this connection."
        )


def size_of_cache(connection: "Connection") -> int:
    """
    Get the total size in bytes of all cache tables.

    Parameters
    ----------
    connection : "Connection"

    Returns
    -------
    int
        Number of bytes in total used by cache tables

    """
    sql = """SELECT sum(table_size(tablename, schema)) as total_bytes 
        FROM cache.cached  
        WHERE NOT cached.class='Table'"""
    cache_bytes = connection.fetch(sql)[0][0]
    return 0 if cache_bytes is None else int(cache_bytes)


def get_max_size_of_cache(connection: "Connection") -> int:
    """
    Get the upper limit set in FlowDB for the cache size, in bytes.

    Parameters
    ----------
    connection : "Connection"

    Returns
    -------
    int
        Number of bytes in total available cache tables

    """
    sql = "SELECT cache_max_size()"
    return int(connection.fetch(sql)[0][0])


def get_cache_half_life(connection: "Connection") -> float:
    """
    Get the current setting for cache half-life.

    Parameters
    ----------
    connection : "Connection"

    Returns
    -------
    float
        Cache half-life setting

    """
    sql = "SELECT cache_half_life()"
    return float(connection.fetch(sql)[0][0])


def set_cache_half_life(connection: "Connection", cache_half_life: float) -> None:
    """
    Set the cache's half-life.

    Parameters
    ----------
    connection : "Connection"
    cache_half_life : float
        Setting for half-life

    Notes
    -----

    Changing this setting without flushing the cache first may have unpredictable consequences
    and should be avoided.
    """
    sql = (
        f"UPDATE cache.cache_config SET value='{cache_half_life}' WHERE key='half_life'"
    )
    with connection.engine.begin() as trans:
        trans.execute(sql)


def set_max_size_of_cache(connection: "Connection", cache_size_limit: int) -> None:
    """
    Get the upper limit set in FlowDB for the cache size, in bytes.

    Parameters
    ----------
    connection : "Connection"
    cache_size_limit : int
        Size in bytes to set as the cache limit

    """
    sql = f"UPDATE cache.cache_config SET value='{cache_size_limit}' WHERE key='cache_size'"
    with connection.engine.begin() as trans:
        trans.execute(sql)


def compute_time(connection: "Connection", query_id: str) -> float:
    """
    Get the time in ms that a cached query took to compute.

    Parameters
    ----------
    connection : "Connection"
    query_id : str
        md5 identifier of the query

    Returns
    -------
    float
        Number of seconds the query took to compute

    """
    try:
        return float(
            connection.fetch(
                f"SELECT compute_time FROM cache.cached WHERE query_id='{query_id}'"
            )[0][0]
            / 1000
        )
    except IndexError:
        raise ValueError(f"Query id '{query_id}' is not in cache on this connection.")


def score(connection: "Connection", query_id: str) -> float:
    """
    Get the current cache score for a cached query.

    Parameters
    ----------
    connection: "Connection"
    query_id : str
        md5 id of the cached query

    Returns
    -------
    float
        Current cache score of this query

    """
    try:
        return float(
            connection.fetch(
                f"""SELECT cache_score_multiplier*((compute_time/1000)/table_size(tablename, schema))
                 FROM cache.cached WHERE query_id='{query_id}'"""
            )[0][0]
        )
    except IndexError:
        raise ValueError(f"Query id '{query_id}' is not in cache on this connection.")
