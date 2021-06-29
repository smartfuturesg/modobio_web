# Odyssey

--- **_A staff application for the client journey_**

This is a Flask based app that serves webpages and an API to the ModoBio staff. The pages contain the intake and data gathering forms for the _client journey_. The [Odyssey](https://en.wikipedia.org/wiki/Odyssey) is the most famous journey of all time! 🤓

## Documentation

Documentation for this package can be found [on GitLab Pages](http://zan.atventures.tech/odyssey/)

## Requirements

To run Odyssey on your local computer, you will need the following installed.

- Python (tested with 3.8)
- pip (should come with Python version 3.4+, if not more info [here](https://pip.pypa.io/en/stable/installing/)). Pip will be used to install all the python dependencies, see [requirements/development.txt](requirements/development.txt) for a full list of dependencies.

The following servers also need to be installed and running on localhost (default ports). In the following list PostgreSQL is absolutely mandatory. The other servers may be skipped, but you will miss important functinoality and you will have to override the default configuration to get the API to run without those servers present.

- PostgreSQL (tested with 13.3)
- Elasticsearch (tested with 7.13.2)
- Redis (tested with 6.2.4)
- Hasura (tested with 1.3.3, see [hasura/README.md](hasura/README.md) for installation instructions)

## Pre-installation

### Prepare PostgreSQL

Use your favourite package manager to install PostgreSQL on your system. [See here](https://phoenixnap.com/kb/how-to-install-postgresql-on-ubuntu) for more information on how to install PostgreSQL on Ubuntu. How to start/stop the PostgreSQL server will depend on your system. For SystemD-based Linux systems (including Ubuntu), use `sudo systemctl <start|stop|restart|status|reload> postgresql-13.service`.

With PostgreSQL installed, create a new database named modobio. For convenience, add a role (user) with the same name as your login name. Because it is a local connection, you should not need a password. If that is not the case, edit `/etc/pg_hba.conf` and set the METHOD column to `trust` for all local connections.

```shell
$ sudo -u postgres createuser -l $USER
$ sudo -u postgres createdb -O $USER modobio
$ psql modobio
modobio=> \q
```

### External libraries

Pip should normally take care of installing all python dependencies, but some dependencies in turn depend on non-python libraries. To install these on Ubuntu Linux:

```shell
$ sudo apt install pkg-config libcairo2-dev libgirepository1.0-dev libpangocairo-1.0-0 postgresql-client
```  

### Virtual Environment

If you want to use a virtual environment to install all the dependencies, use the following command before proceeeding. It helps to avoid conflicts between versions of installed dependencies.

```shell
$ python -m venv <virtual_env_name>
$ source <virtual_env_name>/bin/activate
```

## Installation

Download the code repository from GitLab or use git to clone the repository.

```shell
$ git clone https://gitlab.atventurepartners.tech/zan/odyssey.git
$ cd odyssey
$ pip install -r requirements/development.txt
$ pip install -e .
```

Pip should take care of installing all Python dependencies. The `-e` option means it is installed in _editable_ mode. It imports and runs like it's installed in the normal `PYTHONPATH` directory, but you can edit it in the git repo and see the updates immediately.

## Set the environment

The server can be configured by setting environmental variables before starting the server. The default configuration is in [src/odyssey/default.py]. Each upper case variable in that file will be loaded into the `app.config` dictionary. Each variable can be overridden by setting a variable of the same name in the environment.

Some variables hold passwords or secrets which cannot be stored in code. They have an empty default and **must** be set in the environment before startup or the API will fail to load. The values for these can be found in the shared 1Password vault.

The following list of environmental variables must be set in the environment. For more information, see [src/odyssey/default.py](src/odyssey/default.py) or [the documentation page](http://zan.atventures.tech/odyssey/odyssey/odyssey.config.html)

```shell
$ export PYTHONPATH=</path/to>/odyssey/src
$ export FLASK_APP=odyssey
$ export FLASK_ENV=development
$ export TWILIO_ACCOUNT_SID=...
$ export TWILIO_API_KEY_SID=...
$ export TWILIO_API_KEY_SECRET=...
$ export CONVERSATION_SERVICE_SID=...
$ export OURA_CLIENT_ID=...
$ export OURA_CLIENT_SECRET=...
$ export FITBIT_CLIENT_ID=...
$ export FITBIT_CLIENT_SECRET=...
```

## Database migration

If this is a clean, empty database, use Alembic (through flask-migrate) to push the database schemas changes to your local database.

```shell
$ flask db upgrade
```

If there are errors while trying to upgrade the database, you can use the script `migrations/list_versions.py` to help figuring out which is the offending version script. Most likely someone created a version script, but before it was merged someone else created one too, off of the same endpoint. Resolve the migration conflict and run `flask db upgrade` again.

## Database loading

Some database functionality is loaded directly into PostgreSQL before starting the API server. This includes various lookup tables, stored procedures, and a list of test users. To load these, run the following command.

```shell
$ python database/sql_scriptrunner.py
```

The following section is deprecated. A list of standard test users is added to the database by the SQL scripts. I'm leaving the information here in case anyone needs to a a different user for some reason.

> Before you can log in, you will need to add a staff member to the `Staff` table in the database. At the moment there is no easy admin page to do this. First, generate a password hash. The Flask app uses the `check_password_hash()` function from the `werkzeug.security` module to check the passwords. To generate a compatible password hash, open Python and type the following.
>
> ```python
> >>> from werkzeug.security import generate_password_hash
> >>> generate_password_hash('123')
> 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'
> ```
>
> This is the password hash for password '123'. Copy the string that starts with 'pbkdf2:...'. Then, in a terminal, run the following commands:
>
> ```shell
> $ psql modobio
> modobio => INSERT INTO "Staff" (email, firstname, lastname, fullname, password, is_admin)
>            VALUES ('<email>', 'Name', 'Lastname', 'Name Lastname', '<password>', true);
> modobio => exit
> ```
>
> Replace `<password>` with the SHA string generated above and `<email>` with the email you want to register. You should now be able to log in as 'name@modobio.com' with password '123' (or whatever you used above).

## Start the server

To start the API server, simply execute:

```shell
flask run
```

The app will keep running in the terminal and give extensive debug output. If all is well, navigate your browser to http://localhost:5000. More info on running Flask apps [here](https://flask.palletsprojects.com/en/1.1.x/quickstart/).

# Docker

If you have Docker installed, you can bring up a local, ready to go instance of this application by running the following commands.

```shell
$ docker network create modobio
$ docker run --name postgres_local --network modobio -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=modobio -p 5432:5432 -d postgres
$ docker build -t odyssey .
$ docker run --name odyssey --network modobio -e FLASK_APP=odyssey:create_app -e FLASK_ENV=development -e FLASK_DB_USER=postgres -e FLASK_DB_PASS=password -e FLASK_DB_HOST=postgres_local -e PYTHONPATH=/usr/src/app/src -p 5000:5000 -d odyssey
```

This will build the application, stand up a containerized instance of PostgreSQL, update the database, and run the application for use.
