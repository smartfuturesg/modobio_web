from __future__ import with_statement

import logging
from logging.config import fileConfig
import os
import sys

import boto3
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from flask import current_app
# config.set_main_option(
#     'sqlalchemy.url',
#     str(current_app.extensions['migrate'].db.engine.url).replace('%', '%%'))
target_metadata = current_app.extensions['migrate'].db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# change the database user to the master user for the purpose of editing schemas
ssm = boto3.client('ssm')
db_flav = ssm.get_parameter(Name='/modobio/odyssey/db_flav')['Parameter']['Value']
db_user = ssm.get_parameter(Name='/modobio/odyssey/db_user_master')['Parameter']['Value']
db_pass = ssm.get_parameter(Name='/modobio/odyssey/db_pass_master', WithDecryption=True)['Parameter']['Value']
db_host = ssm.get_parameter(Name='/modobio/odyssey/db_host')['Parameter']['Value']
if os.getenv('FLASK_ENV') == 'development':
    db_name = ssm.get_parameter(Name='/modobio/odyssey/db_name_dev')['Parameter']['Value']
    db_connection_string = f'{db_flav}://{db_user}:{db_pass}@{db_host}/{db_name}'
elif os.getenv('FLASK_ENV') == 'production':
    db_name = ssm.get_parameter(Name='/modobio/odyssey/db_name')['Parameter']['Value']
    db_connection_string = f'{db_flav}://{db_user}:{db_pass}@{db_host}/{db_name}'
elif os.getenv('FLASK_ENV') == 'development_local':
    db_connection_string = str(current_app.extensions['migrate'].db.engine.url).replace('%', '%%')
else:
    print("which database are you upgrading?")
    db_name = input()

print(f"updating/querying database using the following connection string: \m {db_connection_string}")
print("continue?")
answer = input()

if answer not in ['y', 'Y']:
    sys.exit()

config.set_main_option(
    'sqlalchemy.url',
    db_connection_string)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            **current_app.extensions['migrate'].configure_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
