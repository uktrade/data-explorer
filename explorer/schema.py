import logging
from collections import namedtuple

from django.core.cache import cache
from geoalchemy2 import Geometry  # Needed for sqlalchemy to understand geometry columns
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql.array import ARRAY
from sqlalchemy.dialects.postgresql.base import DOUBLE_PRECISION, ENUM, TIMESTAMP, UUID
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.sql.sqltypes import (
    BIGINT,
    BOOLEAN,
    CHAR,
    DATE,
    FLOAT,
    INTEGER,
    NUMERIC,
    SMALLINT,
    String,
    TEXT,
    VARCHAR,
)

from explorer.app_settings import (
    ENABLE_TASKS,
    EXPLORER_ASYNC_SCHEMA,
    EXPLORER_CONNECTIONS,
    EXPLORER_SCHEMA_EXCLUDE_TABLE_PREFIXES,
    EXPLORER_SCHEMA_INCLUDE_TABLE_PREFIXES,
    EXPLORER_SCHEMA_INCLUDE_VIEWS,
)
from explorer.tasks import build_schema_cache_async
from explorer.utils import get_valid_connection

logger = logging.getLogger(__name__)


# These wrappers make it easy to mock and test
def _get_includes():
    return EXPLORER_SCHEMA_INCLUDE_TABLE_PREFIXES


def _get_excludes():
    return EXPLORER_SCHEMA_EXCLUDE_TABLE_PREFIXES


def _include_views():
    return EXPLORER_SCHEMA_INCLUDE_VIEWS is True


def do_async():
    return ENABLE_TASKS and EXPLORER_ASYNC_SCHEMA


def _include_table(t):
    if _get_includes() is not None:
        return any([t.startswith(p) for p in _get_includes()])
    return not any([t.startswith(p) for p in _get_excludes()])


def connection_schema_cache_key(connection_alias):
    return '_explorer_cache_key_%s' % connection_alias


def schema_info(connection_alias, schema=None, table=None):
    key = connection_schema_cache_key(connection_alias)
    ret = cache.get(key)
    if ret:
        return ret
    if do_async():
        build_schema_cache_async.delay(connection_alias, schema, table)
    else:
        return build_schema_cache_async(connection_alias, schema, table)


COLUMN_MAPPING = {
    ENUM: 'Enum',
    CHAR: 'Text',
    VARCHAR: 'Text',
    String: 'Text',
    TEXT: 'Text',
    UUID: 'UUID',
    ARRAY: 'Array',
    INTEGER: 'Integer',
    SMALLINT: 'Integer',
    BIGINT: 'Integer',
    NUMERIC: 'Decimal',
    DOUBLE_PRECISION: 'Decimal',
    FLOAT: 'Decimal',
    BOOLEAN: 'Boolean',
    DATE: 'Date',
    TIMESTAMP: 'Timestamp',
    Geometry: 'Geometry',
}

Column = namedtuple('Column', ['name', 'type'])
Table = namedtuple('Table', ['name', 'columns'])


class TableName(namedtuple("TableName", ['schema', 'name'])):
    __slots__ = ()

    def __str__(self):
        return f'{self.schema}.{self.name}'


def build_schema_info(connection_alias, schema=None, table=None):
    """
        Construct schema information via engine-specific queries of the tables in the DB.

        :return: Schema information of the following form.
            [
                (("db_schema_name", "db_table_name"),
                    [
                        ("db_column_name", "DbFieldType"),
                        (...),
                    ]
                )
            ]

        """
    connection = get_valid_connection(connection_alias)

    engine = create_engine(
        f'postgresql://{connection.settings_dict["USER"]}:{connection.settings_dict["PASSWORD"]}'
        f'@{connection.settings_dict["HOST"]}:{connection.settings_dict["PORT"]}/'
        f'{connection.settings_dict["NAME"]}'
    )
    insp = Inspector.from_engine(engine)
    if schema and table:
        return _get_columns_for_table(insp, schema, table)

    tables = []
    schemas_and_tables = _get_accessible_schemas_and_tables(connection)
    for schema, table_name in schemas_and_tables:
        if not _include_table(table_name):
            continue

        columns = _get_columns_for_table(insp, schema, table_name)
        tables.append(Table(TableName(schema, table_name), columns))

    engine.dispose()
    return tables


def _get_accessible_schemas_and_tables(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            f"""
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema not in %s
ORDER BY table_schema, table_name;
""",
            [('pg_toast', 'pg_temp_1', 'pg_toast_temp_1', 'pg_catalog', 'information_schema')],
        )
        schemas_and_tables = cursor.fetchall()

    return schemas_and_tables


def _get_columns_for_table(insp, schema, table_name):
    columns = []
    cols = insp.get_columns(table_name, schema=schema)
    for col in cols:
        try:
            columns.append(Column(col['name'], COLUMN_MAPPING[type(col['type'])]))
        except KeyError:
            logger.info(
                f'Skipping {col["name"]} as {col["type"]} ({type(col["type"])} '
                f'is not a supported field type'
            )
            continue
    return columns


def build_async_schemas():
    if do_async():
        for c in EXPLORER_CONNECTIONS:
            schema_info(c)
