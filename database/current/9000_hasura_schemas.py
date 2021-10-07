# This file prepares the database for the Hasura GraphQL engine.
#
# Hasura needs two schemas that will hold tables with operational data.
# These tables need to be readable and writeable by the user who accesses
# the data from Hasura (the <username> in the DATABASE_URI). However, the
# user creating these schemas must be superuser.
#
# In other words: the user running sql_scriptrunner.py must be superuser,
# while the user mentioned in this script must be an ordinary user. The
# latter user is not know at development time, and will be replaced upon
# execution by sql_scriptrunner.py. For this reason, this file is a python
# file and not a pure SQL file.
#
# For more info, see:
# https://hasura.io/docs/1.0/graphql/core/deployment/postgres-requirements.html

import os

user = os.getenv('DB_USER')
password = os.getenv('DB_PASS')

# CREATE USER has no IF NOT EXISTS clause, hence the ugly workaround
# https://stackoverflow.com/questions/8092086/create-postgresql-role-user-if-it-doesnt-exist

if user:
    add_password = ''
    if password:
        add_password = f'LOGIN PASSWORD \'{password}\''

    sql = f"""
    DO
    $do$
    BEGIN
        IF NOT EXISTS
            (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{user}')
        THEN
            CREATE ROLE {user} {add_password};
       END IF;
    END
    $do$;

    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    CREATE SCHEMA IF NOT EXISTS hdb_catalog AUTHORIZATION {user};
    CREATE SCHEMA IF NOT EXISTS hdb_views AUTHORIZATION {user};

    GRANT SELECT ON ALL TABLES IN SCHEMA information_schema TO {user};
    GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog TO {user};

    GRANT USAGE ON SCHEMA public TO {user};
    GRANT ALL ON ALL TABLES IN SCHEMA public TO {user};
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO {user};
    GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO {user};
    """
else:
    sql = """
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    CREATE SCHEMA IF NOT EXISTS hdb_catalog;
    CREATE SCHEMA IF NOT EXISTS hdb_views;
    """
