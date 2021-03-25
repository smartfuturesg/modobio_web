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
but it does preserve any number of initial underscores. It does not do any conversion if
the string does not contain any underscores except leading underscores.

Examples
--------

first_name  -> firstName
is_MVP      -> isMvp
guest_      -> guest
_hidden_var -> _hiddenVar
_keepCase   -> _keepCase

Links
-----

https://atventurepartners.atlassian.net/wiki/spaces/AVP/pages/1210548231/Database+Relationships
"""

import pathlib
import yaml

from sqlalchemy import create_engine, inspect

from odyssey.config import database_uri

# File locations
here = pathlib.Path(__file__).parent
hasura_tables_file = here / 'metadata' / 'tables.yaml'
hasura_no_track_file = here / 'metadata' / 'tables-no-track.yaml'

def first_letter(string: str) -> int:
    """ Return the index of the first non-underscore character in a string. """
    n = 0
    while n < len(string) and string[n] == '_':
        n += 1
    return n

def pascal(string: str, preserve_leading: bool=True) -> str:
    """ Convert a string from snake_case to PascalCase.

    Preserves leading underscores, unless preserve_leading=False.
    """
    if not string:
        return string

    p = string.replace('_', ' ').title().replace(' ', '')
    n = 0
    if preserve_leading:
        n = first_letter(string)

    return '_' * n + p

def camel(string: str, preserve_leading: bool=True) -> str:
    """ Convert a string from snake_case to camelCase.

    Preserves leading underscores, unless preserve_leading=False.
    """
    p = pascal(string)

    n = 0
    if preserve_leading:
        n = first_letter(string)

    return '_' * n + p[n].lower() + p[n+1:]

def combine_camel(*words, preserve_leading: bool=True) -> str:
    """ Combine multiple words into a single camelCase string.

    Words not containing underscores are assumed to already be in
    camelCase or PascalCase and their internal case (all letters
    except the first) is preserved.

    Leading underscores are preserved for the first word only, unless
    preserve_leading=False.
    """
    final = []
    for w, word in enumerate(words):
        n = first_letter(word)
        if '_' in word[n:]:
            if w == 0:
                conv = camel(word, preserve_leading=preserve_leading)
            else:
                conv = pascal(word, preserve_leading=False)
        else:
            if w == 0:
                if not preserve_leading:
                    n = 0
                conv = word[n].lower() + word[n + 1:]
            else:
                conv = word
        final.append(conv)
    return ''.join(final)

# Database
db_uri = database_uri(docstring=__doc__)
engine = create_engine(db_uri)
inspector = inspect(engine)

# Read exception file
hasura_no_track = []
with hasura_no_track_file.open() as fh:
    hasura_no_track = yaml.safe_load(fh)

hasura_tables = []
hasura_tables_idx = {}

# First pass: track tables.
for schema in sorted(inspector.get_schema_names()):
    if schema in ('hdb_catalog', 'hdb_views', 'information_schema'):
        continue

    # Views are tables in metadata
    tablenames = inspector.get_table_names(schema=schema)
    tablenames.extend(inspector.get_view_names(schema=schema))
    for tablename in sorted(tablenames):
        # Don't track these tables
        if tablename in hasura_no_track:
            continue

        # Start tracking table by adding it to metadata
        table = {
            'table': {
                'schema': schema,
                'name': tablename
            },
            'configuration': {
                'custom_column_names': {}
            },
            'object_relationships': [],
            'array_relationships': []
        }

        # Add custom column names
        for column in inspector.get_columns(tablename, schema=schema):
            colname = column['name']
            table['configuration']['custom_column_names'][colname] = camel(colname)

        hasura_tables.append(table)
        hasura_tables_idx[f'{schema}-{tablename}'] = len(hasura_tables) - 1

# Second pass: track foreign keys

# Relationship names (object + array) must be unique per table.
relationship_names = set()

for table in hasura_tables:
    # Track foreign keys
    #
    # In Hasura, all relationships are bidirectional.
    #
    # Referring side points to primary key (or column with unique constraint) in
    # other table. This half of the relationship is always an object relationship.
    #
    # Referred side is array (1-to-many), unless column on referring side has
    # unique constraint (1-to-1).
    #
    # Multiple object-array combos is many-to-many.

    schema = table['table']['schema']
    tablename = table['table']['name']

    # Get list of all columns with unique contraint.
    uniq = set()
    for u in inspector.get_unique_constraints(tablename, schema=schema):
        uname = [f'{tablename}'] + [col for col in u['column_names']]
        uniq.add('-'.join(uname))

    # Hasura adds relationships in order of column definition.
    # TODO: this is not true for the situation where multiple foreign keys
    # point to a single primary key, e.g. ClinicalCareTeam has user_id and
    # team_member_user_id and both reference User.user_id. For some reason
    # that order is not alphabetical. Seems reverse, not sure.
    foreign_keys = inspector.get_foreign_keys(tablename, schema=schema)
    columns = inspector.get_columns(tablename, schema=schema)
    foreign_keys_ordered = []
    for col in columns:
        for fk in foreign_keys:
            if col['name'] in fk['constrained_columns']:
                foreign_keys_ordered.append(fk)

    for fk in foreign_keys_ordered:
        # Foreign names and tables
        f_schema = fk['referred_schema']
        f_tablename = fk['referred_table']
        f_schema_table = f'{f_schema}-{f_tablename}'
        f_idx = hasura_tables_idx[f_schema_table]
        f_table = hasura_tables[f_idx]

        # TODO: What to do when either one of the sides of a
        # foreign key involves more than 1 column?
        f_column = fk['referred_columns'][0]
        column = fk['constrained_columns'][0]

        ### Referring side

        # Set unique name for object relationship
        #  1. foreign tablename is singularized (simple name)
        #  2. if an object relation with simple name already
        #     exists on this table: foreignTableByForeignColumn
        #     where foreignTable is the full (non-singularized) name.
        relationship_name = f_tablename
        if f_tablename.endswith('ies'):
            relationship_name = f_tablename[:-3] + 'y'
        elif f_tablename.endswith('s'):
            relationship_name = f_tablename[:-1]

        idx_name = f'{tablename}-{relationship_name}'
        if idx_name in relationship_names:
            relationship_name = combine_camel(f_tablename, 'By', column)
            idx_name = f'{tablename}-{relationship_name}'

        relationship_names.add(idx_name)

        # Referring side, always object
        obj = {
            'name': relationship_name,
            'using': {
                'foreign_key_constraint_on': column
            }
        }

        table['object_relationships'].append(obj)

        ### Referred side

        # Forced one-to-one relationship.
        if f'{tablename}-{column}' in uniq:
            # Set unique name for object relationship; sides have switched.
            relationship_name = tablename
            if tablename.endswith('ies'):
                relationship_name = tablename[:-3] + 'y'
            elif tablename.endswith('s'):
                relationship_name = tablename[:-1]

            idx_name = f'{f_tablename}-{relationship_name}'
            if idx_name in relationship_names:
                relationship_name = combine_camel(tablename, 'By', column)
                idx_name = f'{f_tablename}-{relationship_name}'

            relationship_names.add(idx_name)

            obj = {
                'name': relationship_name,
                'using': {
                    'manual_configuration': {
                        'remote_table': {
                            'schema': schema,
                            'name': tablename
                        },
                        'column_mapping': {
                            f_column: column
                        }
                    }
                }
            }

            f_table['object_relationships'].append(obj)
        else:
            # Set unique name for array relationship; pluralize first.
            relationship_name = tablename
            if tablename.endswith('y'):
                relationship_name = tablename[:-1] + 'ies'
            elif not tablename.endswith('s'):
                relationship_name += 's'

            idx_name = f'{f_tablename}-{relationship_name}'
            if idx_name in relationship_names:
                relationship_name = combine_camel(tablename, 'By', column)
                idx_name = f'{f_tablename}-{relationship_name}'

            relationship_names.add(idx_name)

            arr = {
                'name': relationship_name,
                'using': {
                    'foreign_key_constraint_on': {
                        'column': column,
                        'table': {
                            'schema': schema,
                            'name': tablename
                        }
                    }
                }
            }

            f_table['array_relationships'].append(arr)

# Third pass: remove empty, sort non-empty
for table in hasura_tables:
    if not table['array_relationships']:
        table.pop('array_relationships')
    else:
        table['array_relationships'].sort(key=lambda r: r['name'])

    if not table['object_relationships']:
        table.pop('object_relationships')
    else:
        table['object_relationships'].sort(key=lambda r: r['name'])

    if table['configuration']:
        if not table['configuration']['custom_column_names']:
            table['configuration'].pop('custom_column_names')
            if not table['configuration']:
                table.pop('configuration')

with hasura_tables_file.open(mode='wt') as fh:
    yaml.dump(hasura_tables, stream=fh, sort_keys=False, default_flow_style=False)
