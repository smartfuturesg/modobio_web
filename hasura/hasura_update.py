#!/usr/bin/env python
"""Update Hasura metadata.

This script updates Hasura metadata. The following actions are taken:

1. Track untracked tables in the database.
2. Set custom column names, displaying snake_case columns as camelCase.

This script should be run manually by the developer after a schema update. The resulting
changes to tables.yaml should be included in the merge.

1. Table tracking
-----------------

A special file `tables-no-track.yaml` exists in the `metadata/` directory. It is not
part of the Hasura metadata. It contains a list of table names that should not be tracked.

2. Column names
---------------

Column name conversion does not preserve case within the string or trailing underscores,
but it does preserve any number of initial underscores.

Examples
--------
first_name  -> firstName
is_MVP      -> isMvp
guest_      -> guest
_hidden_var -> _hiddenVar
"""

import pathlib
import yaml

from sqlalchemy import create_engine, inspect

from odyssey.config import database_uri

# File locations
here = pathlib.Path(__file__).parent
hasura_tables_file = here / 'metadata' / 'tables.yaml'
hasura_no_track_file = here / 'metadata' / 'tables-no-track.yaml'

def snake_to_camel(string: str) -> str:
    if not string:
        return string

    pascal = string.replace('_', ' ').title().replace(' ', '')
    camel = pascal[0].lower() + pascal[1:]

    n = 0
    while n < len(string) and string[n] == '_':
        n += 1
    return '_' * n + camel

# Database
db_uri = database_uri(docstring=__doc__)
engine = create_engine(db_uri)
inspector = inspect(engine)

# Read files
hasura_tables = []
with hasura_tables_file.open() as fh:
    hasura_tables = yaml.safe_load(fh)

hasura_tablenames = {h["table"]["schema"] + '-' + h["table"]["name"]: n for n, h in enumerate(hasura_tables)}

hasura_no_track = []
with hasura_no_track_file.open() as fh:
    hasura_no_track = yaml.safe_load(fh)

# loop schemas/tables/column
for schema in inspector.get_schema_names():
    if schema in ('hdb_catalog', 'hdb_views', 'information_schema'):
        continue

    for table in inspector.get_table_names(schema=schema):
        # Don't track these tables
        if table in hasura_no_track:
            continue

        schema_table = f'{schema}-{table}'
        if schema_table not in hasura_tablenames:
            # Start tracking table by adding it to metadata
            tracked_table = {
                'table': {
                    'name': table,
                    'schema': schema
                },
                'object_relationships': []
            }
            
            # Track foreign keys
            for fk in inspector.get_foreign_keys(table, schema=schema):
                rel = {
                    'name': fk['referred_table'],
                    'using': {
                        'foreign_key_constraint_on': fk['referred_columns']
                    }
                }
                tracked_table['object_relationships'].append(rel)

            hasura_tables.append(tracked_table)
        else:
            # Use already tracked table
            idx = hasura_tablenames[schema_table]
            tracked_table = hasura_tables[idx]

        if 'configuration' not in tracked_table:
            tracked_table['configuration'] = {}
        if 'custom_column_names' not in tracked_table['configuration']:
            tracked_table['configuration']['custom_column_names'] = {}

        # Add custom column names
        for column in inspector.get_columns(table, schema=schema):
            colname = column['name']
            tracked_table['configuration']['custom_column_names'][colname] = snake_to_camel(colname)

with hasura_tables_file.open(mode='wt') as fh:
    yaml.dump(hasura_tables, stream=fh)
