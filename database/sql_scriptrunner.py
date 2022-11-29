#!/usr/bin/env python
"""Collect SQL statements from .sql and .py files and execute them on a database.

This script recursively finds all .sql and .py files (excluding this script itself) stored
in this directory and its subdirectories. There are 3 categories of scripts:

1. Files from previous releases, under the 'release-x.y/' subdirectories.
2. Files from the current development cycle, under the 'current/' subdirectory.
3. Files for development only, under the 'dev/' subdirectory.

All files in each category (.sql and .py combined) will be executed in lexicographical
order. Use a numerical prefix to force a certain order. The categories will be executed
in the order given above.

By default, categories 1 and 3 are included in DEV and TESTING environments and excluded
in PRODUCTION. Use ``--previous`` and ``--dev``, respectively, to include these
categories despite the environment.

The .sql files should contain raw SQL statements. The SQL in those files will be executed
directly on the database. The .py files should contain a variable ``sql`` which will be
imported by this script. The ``sql`` variable should contain one or more SQL statements.
The difference with .sql files is that python will execute any code in the main scope of
the script upon import, which can be used to change the SQL code at runtime. For example
to substitute a username which is only available from the environment at runtime.
"""

import importlib
import pathlib
import boto3
from sqlalchemy import create_engine, text

from odyssey.config import Config, database_parser

# Load config from API.
conf = Config()

# Get DB options.
parser = database_parser()
parser.description = __doc__ + '\n' + parser.description

parser.add_argument(
    'scripts',
    nargs='*',
    help='[Optional] Individual scripts to be run. Only the given scripts are run and nothing else. '
         'Environment setting (development vs production) or any of the optional arguments are ignored.')

prev_group = parser.add_mutually_exclusive_group()
prev_group.add_argument(
    '--previous',
    action='store_true',
    help='Include scripts from all previous releases. Searches all "release-x.y/" subdirectories. '
         'Defaults to True when FLASK_ENV=development, False otherwise.')
prev_group.add_argument(
    '--no-previous',
    action='store_false',
    help='Negate the options of --previous. Do NOT include scripts from previous releases when '
         'FLASK_ENV=development.')

current_group = parser.add_mutually_exclusive_group()
current_group.add_argument(
    '--current',
    action='store_true',
    help='Include scripts from the current development cycle. This does not depend on the '
         'environment and is always True. Using this option has no effect, it is included '
         'for completion.')
current_group.add_argument(
    '--no-current',
    action='store_false',
    help='Do NOT run the scripts from the current development cycle. This does not depend '
         'on the environment and always defaults to False. May be useful during development '
         'of the scripts.')

dev_group = parser.add_mutually_exclusive_group()
dev_group.add_argument(
    '--dev',
    action='store_true',
    help='Include development scripts, all scripts under the "dev/" subdirectory. '
         'Defaults to True when FLASK_ENV=development, False otherwise.')
dev_group.add_argument(
    '--no-dev',
    action='store_false',
    help='Negate the options of --dev. Do NOT include development scripts when '
         'FLASK_ENV=development.')

parser.add_argument(
    '--demo',
    action='store_true',
    help='Run extra scripts from the "demo/" subdirectory. Intended for the demo environment.')

args = parser.parse_args()

# Collect files.
files = args.scripts
if not files:
    # if args.previous == args.no_previous (i.e. both are True or both are False)
    # then --prev or --no-prev was given. Otherwise, no option was given so go by env.
    prev = dev = conf.DEV
    if args.previous == args.no_previous:
        prev = args.previous

    if args.dev == args.no_dev:
        dev = args.dev

    cur = True
    if args.current == args.no_current:
        cur = args.current

    files = []
    here = pathlib.Path(__file__).parent

    if prev:
        prev_dir = here / 'releases'
        prev_sql_files = list(prev_dir.rglob('*.sql'))
        prev_py_files = list(prev_dir.rglob('*.py'))

        prev_sql_files.extend(prev_py_files)

        prev_sql_files.sort()
        files.extend(prev_sql_files)

    if cur:
        current_dir = here / 'current'
        current_sql_files = list(current_dir.glob('*.sql'))
        current_py_files = list(current_dir.glob('*.py'))

        current_sql_files.extend(current_py_files)
        current_sql_files.sort()
        files.extend(current_sql_files)

    if dev:
        dev_dir = here / 'dev'
        dev_sql_files = list(dev_dir.glob('*.sql'))
        dev_py_files = list(dev_dir.glob('*py'))

        dev_sql_files.extend(dev_py_files)
        dev_sql_files.sort()
        files.extend(dev_sql_files)

if args.demo:
    demo_dir = pathlib.Path(__file__).parent / 'demo'
    demo_sql_files = list(demo_dir.glob('*.sql'))
    demo_py_files = list(demo_dir.glob('*py'))
    demo_sql_files.extend(demo_py_files)
    demo_sql_files.sort()
    files.extend(demo_sql_files)

# Open DB connection.
print(f'Using the following database: {args.db_uri}')
engine = create_engine(args.db_uri)

with engine.connect() as conn:
    for f in files:
        if f.name == '__init__.py':
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

            # mod = importlib.import_module(modname) stopped working for no apparent reason,
            # but the following does work.
            spec = importlib.util.spec_from_file_location(modname, f.as_posix())
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            if hasattr(mod, 'sql'):
                conn.execute(text(mod.sql))
                conn.execute(text('commit;'))
            print('done')
        else:
            print('skipped')
