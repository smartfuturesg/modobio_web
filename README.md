# Odyssey, the staff application for the client journey

This is a Flask based app that server webpages to the ModoBio staff. The pages contain the intake and data gathering forms for the _client journey_.

## Requirements

For testing on local computer.

- Postgres server on localhost with a database named "modobio"
- Python (tested with 3.7)
- pip

## Installation

Pull this git repo, then (assuming bash shell):

```shell
cd odyssey
pip -e install .
export FLASK_APP=odyssey
export FLASK_ENV=development
flask run
```

If all is well, navigate your browser to http://localhost:5000

More info on running Flask apps [here](https://flask.palletsprojects.com/en/1.1.x/quickstart/)
