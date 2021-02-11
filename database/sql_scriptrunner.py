#!/usr/bin/env python
"""Collect SQL statements from .sql and .py files and execute them on a database.

This script finds all .sql and .py files (excluding this script itself) stored in this
directory. The .sql files should contain raw SQL statements. The SQL in those files will
be executed directly on the database.

The .py files should contain a variable `sql` which will be imported by this script. The `sql` variable should contain one or more SQL statements. The difference with .sql files is that
python will execute any code in the main scope of the script upon import, which can be used
to change the SQL code at runtime. For example to substitute a password which is only
available from the environment at runtime.

All files (.sql and .py combined) will be parsed in lexicographical order. Use a numerical
prefix to force a certain order.

Pass the URI of the database with the command line argument `--db_uri`. If no URI is
provided, environmental variables will be used to create a URI.

    DB_FLAV: the database "flavour", postgres by default.
    DB_USER: the database username, empty by default.
    DB_PASS: the password for the user, empty by default.
    DB_HOST: the hostname or IP address of the database server, localhost by default.
    DB_NAME: the name of the database, modobio by default.

Or, specify the entire URI in one string as

    DB_URI: no default, e.g. postgres://user@password:localhost/modobio
"""

import argparse
import importlib
import os
import pathlib

from sqlalchemy import create_engine, text

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument('--db_uri', help="Database URI postgres://<user>:<pass>@<host>/<db>")
args = parser.parse_args()

DB_URI = os.getenv('DB_URI', args.db_uri)

if not DB_URI:
    db_user = os.getenv('DB_USER', '')
    db_pass = os.getenv('DB_PASS', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_flav = os.getenv('DB_FLAV', 'postgresql')
    db_name = os.getenv('DB_NAME', 'modobio')

    DB_URI = f'{db_flav}://{db_user}:{db_pass}@{db_host}/{db_name}'

print(f'Using the following database: {DB_URI}')

engine = create_engine(DB_URI)

current_file = pathlib.Path(__file__)
current_dir = current_file.parent
sql_files = list(current_dir.glob('*.sql'))
py_files = list(current_dir.glob('*.py'))

files = sorted(sql_files + py_files)

with engine.connect() as conn:
    for f in files:
        if f.name == current_file.name:
            continue

        print(f'Processing {f}... ', end='')
        if f.suffix == '.sql':
            with f.open() as fh:
                conn.execute(text(fh.read()))
                # In some situations with comments in the text, there is no
                # commit issued. Do it now. Multiple commits doesn't hurt.
                conn.execute('commit;')
            print('done')
        elif f.suffix == '.py':
            modname = f.stem
            mod = importlib.import_module(modname)
            conn.execute(text(mod.sql))
            conn.execute('commit;')
            print('done')
        else:
            print('skipped')
