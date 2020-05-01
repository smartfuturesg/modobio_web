# Odyssey

--- **_A staff application for the client journey_**

This is a Flask based app that serves webpages to the ModoBio staff. The pages contain the intake and data gathering forms for the _client journey_. The [Odyssey](https://en.wikipedia.org/wiki/Odyssey) is the most famous journey of all time! 🤓

## Requirements

For testing on your local computer, you will need the following installed.

- Postgres server on localhost with a database named "modobio" (tested with PostgreSQL 12.2)
- Python (tested with 3.7)
- pip (should come with Python version 3.4+, if not more info [here](https://pip.pypa.io/en/stable/installing/))

## Installation

Open a terminal and (assuming bash shell) run the following commands:

```shell
git clone git@gitlab.atventurepartners.tech:zan/odyssey.git
cd odyssey
pip -e install .
```

Pip should take care of installing all Python dependencies. The `-e` option means you installed it in _editable_ mode. It imports and runs like it's installed in the normal `PYTHONPATH` directory, but you can edit it in the git repo and see the updates immediately.

## Running

In a terminal (assuming bash) type:

```shell
export FLASK_APP=odyssey
export FLASK_ENV=development
flask run
```

The app will keep running in the terminal and give extensive debug output. If all is well, navigate your browser to http://localhost:5000

More info on running Flask apps [here](https://flask.palletsprojects.com/en/1.1.x/quickstart/)

The flask app will create all necessary tables in the database upon first start. It will **not** update existing tables (Alembic is a separate program to do that). After the tables are created, you will need to add a staff member to the `Staff` table in the database. At the moment, no easy admin page exists yet, so you will need to do this directly in psql (the PostgeSQL command line interface).

Before you can add a staff member, you will need to generate the password hash. The Flask app uses the `check_password_hash()` function from the `werkzeug.security` module to check the passwords. To generate a compatible password hash, open Python and type the following.

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
