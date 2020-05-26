""" Odyssey

*Staff application for the client journey*

This is a `Flask <https://flask.palletsprojects.com>`_ based app that serves webpages to the `ModoBio <https://modobio.com>`_ staff. The pages contain the intake and data gathering forms for the *client journey*. The `Odyssey <https://en.wikipedia.org/wiki/Odyssey>`_ is of course the most famous journey of all time! 🤓
"""

import os
import boto3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

__version__ = '0.0.3'

app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'development':
    app.secret_key = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/modobio'
else:
    ssm = boto3.client('ssm')
    param = ssm.get_parameter(Name='/modobio/odyssey/db_flav')
    db_flav = param['Parameter']['Value']
    param = ssm.get_parameter(Name='/modobio/odyssey/db_user')
    db_user = param['Parameter']['Value']
    param = ssm.get_parameter(Name='/modobio/odyssey/db_pass', WithDecryption=True)
    db_pass = param['Parameter']['Value']
    param = ssm.get_parameter(Name='/modobio/odyssey/db_host')
    db_host = param['Parameter']['Value']
    param = ssm.get_parameter(Name='/modobio/odyssey/db_name')
    db_name = param['Parameter']['Value']

    if os.getenv('FLASK_ENV') == 'testing':
        param = ssm.get_parameter(Name='/modobio/odyssey/db_name_test')
        db_name = param['Parameter']['Value']

    app.config['SQLALCHEMY_DATABASE_URI'] = f'{db_flav}://{db_user}:{db_pass}@{db_host}/{db_name}'

    param = ssm.get_parameter(Name='/modobio/odyssey/app_secret', WithDecryption=True)
    app.secret_key = param['Parameter']['Value']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Custom method to easily update db table from a dict
def _update(self, form: dict):
    for k, v in form.items():
        setattr(self, k, v)

db.Model.update = _update

import odyssey.models

db.create_all()

# Override wtforms.DateTimeField so that it outputs <input type="date"> by default.
import wtforms
class DateInput(wtforms.widgets.Input):
    input_type = 'date'

wtforms.DateTimeField.widget = DateInput()

from odyssey.views.menu import menu

@app.context_processor
def render_menu():
    return {'menu': menu}

from odyssey.views.main import bp
app.register_blueprint(bp)

from odyssey.views.intake import bp
app.register_blueprint(bp, url_prefix='/intake')

from odyssey.views.doctor import bp
app.register_blueprint(bp, url_prefix='/doctor')

from odyssey.views.pt import bp
app.register_blueprint(bp, url_prefix='/pt')

