#!/usr/bin/env python
"""Collect SQL statements from .sql and .py files and execute them on a database.

This script finds all .sql and .py files (excluding this script itself) stored in this
directory. The .sql files should contain raw SQL statements. The SQL in those files will
be executed directly on the database.

The .py files should contain a variable `sql` which will be imported by this script. The
`sql` variable should contain one or more SQL statements. The difference with .sql files is that
python will execute any code in the main scope of the script upon import, which can be used
to change the SQL code at runtime. For example to substitute a password which is only
available from the environment at runtime.

Any files in the `dev/` subdirectory will be executed **only** in DEV or TESTING environments,
not in a PRODUCTION environment.

All files (.sql and .py combined) will be parsed in lexicographical order. Use a numerical
prefix to force a certain order.
"""

import importlib
import pathlib

# from flask import Config as FlaskConfig
from sqlalchemy import create_engine, text

from odyssey.config import database_uri, Config

# Who am I? Where am I?
current_file = pathlib.Path(__file__)
current_dir = current_file.parent

# Load Flask config from API.
# conf = FlaskConfig(current_dir.as_posix())
# conf.from_object(Config())
conf = Config()

# Open DB connection.
db_uri = database_uri(docstring=__doc__)
print(f'Using the following database: {db_uri}')

engine = create_engine(db_uri)

# Collect files.
sql_files = list(current_dir.glob('*.sql'))
py_files = list(current_dir.glob('*.py'))

files = sql_files + py_files

if conf.DEV:
    dev_dir = current_dir / 'dev'
    dev_sql_files = list(dev_dir.glob('*.sql'))
    dev_py_files = list(dev_dir.glob('*py'))

    files.extend(dev_sql_files)
    files.extend(dev_py_files)

# Sort by filename, ignore path
files.sort(key=lambda p: p.name)

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
                conn.execute(text('commit;'))
            print('done')
        elif f.suffix == '.py':
            modname = f.stem
            mod = importlib.import_module(modname)
            conn.execute(text(mod.sql))
            conn.execute(text('commit;'))
            print('done')
        else:
            print('skipped')
