import logging
import os
import sys

import boto3

from alembic import context
from flask import current_app
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from odyssey.config import Config

logger = logging.getLogger(__name__)

# Load config from alembic.ini
# Even though all of our configuration comes from odyssey.config,
# this config object will still hold the config for alembic.
config = context.config

# Load config from the API.
current_app.config.from_object(Config())
db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']



# Load metadata from sqlalchemy
target_metadata = current_app.extensions['migrate'].db.metadata

if not current_app.config['TESTING']: 
    print(f'\n***\nUpdating the database at URI: \n {db_uri}')
    print('Continue? [Y,n]')
    answer = input()

    if answer not in ('y', 'Y'):
        sys.exit()

config.set_main_option('sqlalchemy.url', db_uri)

def run_migrations_offline():
    """ Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """ Run migrations in 'online' mode.

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
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            compare_type=True,
            **current_app.extensions['migrate'].configure_args)

        with context.begin_transaction():
            if current_app.config['TESTING']: 
                try:
                    context.run_migrations()
                except:
                    raise BaseException
            else:
                context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
