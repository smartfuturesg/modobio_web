# Database preparation

This directory holds scripts that prepare the database before the start of the API. The scripts are loaded by `sql_scriptrunner.py`. The script runner has several command line options, run `./sql_scriptrunner.py --help` for more information.

The scripts in this directory can be of two types: raw SQL (.sql) or Python (.py). Both contain SQL statements which will be executed on the database. The difference is that the Python files can contain extra logic to change the SQL statement at runtime. This can be used, for example, for setting a username that is only known at runtime.

There are 3 categories of scripts, each in their own subdirectory:

1. Previous releases (`releases/`)
2. Current development cycle (`current/`)
3. Development-only files (`dev/`)

When adding new files, they should go into `current/`. Files are sorted lexicographically. We use the convention of a 4-digit numerical prefix to force a known execution order. For convenience, only use factors of 10 in the file numbering, this leave enough "space" between the files to add new ones without having to rename all of them.

The database in production is persistent. That means that these scripts are only ever run once on the production database. When the development cycle is closed and pushed through production, all files in `current/` should be moved to `releases/release-x.y/` and a new development cycle can be started.

Files under `dev/` should only be used for development and never in production. They contain things such as test users, etc.
