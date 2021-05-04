# Hasura

[Hasura](https://hasura.io) is an engine that can handle [GraphQL](https://graphql.org) requests. This directory holds information to persist the Hasura setup. The `metadata/` subdirectory holds the metadata of the Hasura setup. Metadata is information about the setup that is not the SQL schemas or data, but information such as which tables are tracked by Hasura, custom actions, authorization information, etc.

Since we use flask-migrate/alembic to migrate the database, we will **not** use the `migrations/` subdirectory. It should remain empty. The `seeds/` subdirectory may hold database data (e.g. test user, staff member) in sql format. 

## Setup

In our setup, Hasura connects to an existing database. [See here](https://gitlab.atventurepartners.tech/zan/odyssey/README.md) to learn how to set up a postgresql database. For general Hasura information, [see here](https://hasura.io/docs/1.0/graphql/core/index.html)

### Prepare database

Hasura needs a couple of special schemas present in the database. They get created when the database is initialized by [database/sql_scriptrunner.py](https://gitlab.atventurepartners.tech/zan/odyssey/database/sql_scriptrunner.py), but if you don't want to start from scratch, run these lines by hand in `psql`:

```sql
CREATE EXTENSION pgcrypto;
CREATE SCHEMA hdb_catalog AUTHORIZATION [username];
CREATE SCHEMA hdb_views AUTHORIZATION [username];
```
where \[username\] is the name of the database user with access from Hasura.

### Install Hasura

Hasura is installed through docker. Make sure you have docker installed first. Then:

```shell
docker run -d -p 8080:8080 \
    -e HASURA_GRAPHQL_DATABASE_URL=postgres://[username]:[password]@[host_ip]/[dbname] \
    -e HASURA_GRAPHQL_ADMIN_SECRET=[somesecret] \
    -e HASURA_GRAPHQL_ENABLE_CONSOLE=true \
    -e HASURA_GRAPHQL_ENABLE_TELEMETRY=false \
    -e HASURA_GRAPHQL_JWT_SECRET='{ \
        "type": "HS256", \
        "key": "[SECRET_KEY]", \
        "claims_map": { \
            "x-hasura-allowed-roles": { \
                "path": "$.x-hasura-allowed-roles" \
            }, \
            "x-hasura-default-role": { \
                "path":"$.utype" \
            }, \
            "x-hasura-user-id": { \
                "path":"$.x-hasura-user-id" \
            } \
        } \
    }'
    -v [/path/to]/odyssey/hasura/metadata:/hasura-metadata \
    --name hasura \
    hasura/graphql-engine:latest
```

where \[username\] is the username of the user who can access the database with password \[password\], \[host_ip\] is `localhost` or a different local IP address depending on your docker setup, \[dbname\] is the name of the database (usually `modobio`), \[somesecret\] is a password for admin login to the console, and \[/path/to\] is the path to this directory in the Odyssey source. When all is set up, open the Hasura console in a browser at [](http://localhost:8080) (or \[host_ip\]).

For preparing hasura to expect JWTs for authentication, we must pass the `HASURA_GRAPHQL_JWT_SECRET` environment variable. In hasura we use the same authentication tokens as the ones we use for our API. This environment variable uses a json-style format to provide details on how to decode and extract data from the JWT payload. 

`type` and `key` are the type of JWT encryption algorithm we use and the key used to sign the token; both are required. `key` must be the same as the `SECRET_KEY` config variable used in Flask config. It must also be at least 32 characters long when used with the HS256 algorithm. The `claims_map` is used to help hasura navigate our JWT payload to extract some details required by the hasura authentication system. Only `x-hasura-allowed-roles` and `x-hasura-default-role` are required by hasura. Additionally, we use the `x-hasura-user-id` field as part of our own custom authentication scheme. For more details on hasura authentication visit the documentation on [authenticating with JWTs](https://hasura.io/docs/latest/graphql/core/auth/authentication/jwt.html)

### Hasura CLI

There are multiple ways to interact with Hasura. The console accessed through the browser is the main way to interact with Hasura for development. Hasura also has a command line interface (CLI), which has to be used for importing and exporting metadata. [Download the CLI here](https://github.com/hasura/graphql-engine/releases/latest). Scroll down to the bottom of the page and download `cli-hasura-[your_os]`. Don't worry about the `cli-ext-hasura`, it will be downloaded by the CLI if and when needed. On Linux/macOS do:

```shell
$ sudo cp ~/Downloads/cli-hasura-xxx /usr/local/bin/hasura
$ sudo chmod +x /usr/local/bin/hasura
```

Hasura CLI will periodically check for updates and warn you when updates are available. This includes betas and is very annoying, not to mention time consuming. On top of that, Hasura sends anonymous (or so they say) telemetry data back to Hasura HQ. To disable update checks and telemetry, run the hasura command once. This will create a config file `~/.hasura/config.json`. Edit this file and set both `show_update_notification` and `enable_telemetry` to `false`.

Hasura CLI needs to be run from this directory to pick up the configuration in `config.yaml`. Do **not** edit `config.yaml`.

- If Hasura is running at a \[host_ip\] other than `localhost`, add `--endpoint http://[host_ip]:8080` or set `export HASURA_GRAPHQL_ENDPOINT="http://[host_ip]:8080"`.
- If you set an admin secret, add `--admin-secret [secret]` or set `export HASURA_GRAPHQL_ADMIN_SECRET="[secret]"`.


### Autotracking

Tables added to the database are not automatically tracked (made visible) by Hasura. The `hasura_update.py` script was written to automatically track all tables and foreign keys in the table. It should be run once immediately after Hasura startup. The script will populate the `metadata/tables.yaml` file.

1. Add any tables that should **not** be tracked to `metadata/tables-no-track.yaml`.
2. Start the Hasura server.
3. Run `$ ./hasura_update.py`. The script needs access to the database. If the database is not accessible on localhost on the normal port, provide a database URI by setting `DB_URI=...` in the environment.
4. Run `$ hasura-cli metadata apply`.

