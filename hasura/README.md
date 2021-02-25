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
    -v [/path/to]/odyssey/hasura/metadata:/hasura-metadata
    --name hasura \
    hasura/graphql-engine:latest
```

where \[username\] is the username of the user who can access the database with password \[password\], \[host_ip\] is `localhost` or a different local IP address depending on your docker setup, \[dbname\] is the name of the database (usually `modobio`), \[somesecret\] is an optional but recommended password for admin login to the console, and \[/path/to\] is the path to this directory in the Odyssey source. When all is set up, open the Hasura console in a browser at [](http://localhost:8080) (or \[host_ip\]).

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


### Workflow

1. Edit the models, create migration scripts, upgrade migration so that the database is at latest version.
2. In Hasura console > settings (cog wheel) > click Reload metadata, to make the changes visible in the console.
3. Edit how you want graphql to interact with the database in the console.
4. If you added tables you do **not** want accessible in graphql, add them to metadata/tables-no-track.yaml.
5. When done, export metadata from the command line: `$ hasura metadata export`.
6. Add custom column names: `$ ./hasura_update.py`.
7. Apply the updated metadata: `$ hasura metadata apply`.
8. Reload the browser tab with Hasura console to see the custom column names (in camelCase).
9. Export the metadata once again: `$ hasura metadata export`.

Steps 7 and 9 may seem redundant, but it helps to discover inconsistent metadata created by the script. Hasura also has a specific order in which metadata is exported, which makes the number of changes in git diff smaller.
