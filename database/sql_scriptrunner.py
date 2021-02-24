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
"""

import importlib
import pathlib

from sqlalchemy import create_engine, text

from odyssey.config import database_uri

db_uri = database_uri(docstring=__doc__)
print(f'Using the following database: {db_uri}}')

engine = create_engine(db_uri)

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
