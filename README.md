# Odyssey

--- **_A staff application for the client journey_**

This is a Flask based app that serves webpages and an API to the ModoBio staff. The pages contain the intake and data gathering forms for the _client journey_. The [Odyssey](https://en.wikipedia.org/wiki/Odyssey) is the most famous journey of all time! 🤓

## Documentation

Documentation for this package can be found [on GitLab Pages](http://zan.atventures.tech/odyssey/)

## Requirements

For testing on your local computer, you will need the following installed.

- Postgres server running on localhost (tested with PostgreSQL 12.2)
- Python (tested with 3.7)
- pip (should come with Python version 3.4+, if not more info [here](https://pip.pypa.io/en/stable/installing/))

## Pre-installation

### Postgres

With postgres installed, create a new database named modobio. For convenience, add a role (user) with the same name as your login name. Because it is a local connection, you should not need a password.

```shell
$ sudo -u postgres createdb modobio
$ sudo -u postgres createuser -l $USER
$ psql modobio
modobio=> \q
```

### External libraries

Pip should normally take care of installing all python dependencies, but some dependencies in turn depend on non-python libraries. To install these on Ubuntu Linux:

```shell
$ sudo apt install pkg-config libcairo2-dev libgirepository1.0-dev libpangocairo-1.0-0 postgresql-client
```  

## Installation

```shell
git clone git@gitlab.atventurepartners.tech:zan/odyssey.git
cd odyssey
pip install -e .
```

Pip should take care of installing all Python dependencies. The `-e` option means you installed it in _editable_ mode. It imports and runs like it's installed in the normal `PYTHONPATH` directory, but you can edit it in the git repo and see the updates immediately.

## Updating the database

If the database schemas have changed between updates, and before the first run, use Alembic (through flask-migrate) to push the changes to your local database.

```shell
export FLASK_APP=odyssey:create_app
export FLASK_ENV=development
export FLASK_DEV=local
flask db migrate
```

## Running

```shell
export FLASK_APP=odyssey:create_app
export FLASK_ENV=development
export FLASK_DEV=local
flask run
```

The app will keep running in the terminal and give extensive debug output. If all is well, navigate your browser to http://localhost:5000

More info on running Flask apps [here](https://flask.palletsprojects.com/en/1.1.x/quickstart/)

Before you can log in, you will need to add a staff member to the `Staff` table in the database. At the moment there is no easy admin page to do this. First, generate a password hash. The Flask app uses the `check_password_hash()` function from the `werkzeug.security` module to check the passwords. To generate a compatible password hash, open Python and type the following.

```python
>>> from werkzeug.security import generate_password_hash
>>> generate_password_hash('123')
'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'
```

This is the password has for password '123'. Copy the string that starts with 'pbkdf2:...'. Then, in a terminal, run the following commands:

```shell
$ psql modobio
modobio => INSERT INTO "Staff" (email, firstname, lastname, fullname, password)
           VALUES ('name@modobio.com', 'Name', 'Lastname', 'Name Lastname', '<password>');
modobio => exit
```

Use the string from the Python output above in place of `<password>`. You should now be able to log in as 'name@modobio.com' with password '123' (or whatever you used above).

### Docker

If you have Docker installed, you can bring up a local, ready to go instance of this application by running the following commands.

```
docker network create modobio
docker run --name postgres_local --network modobio -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=modobio -p 5432:5432 -d postgres
docker build -t odyssey .
docker run --name odyssey --network modobio -e FLASK_APP=odyssey:create_app -e FLASK_ENV=development -e FLASK_DEV=local -e FLASK_DB_USER=postgres -e FLASK_DB_PASS=password -e FLASK_DB_HOST=postgres_local -e PYTHONPATH=/usr/src/app/src -p 5000:5000 -d odyssey
```

This will build the application, stand up a containerized instance of Postgres, update the database, and run the application for use.
