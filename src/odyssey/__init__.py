""" Odyssey

*Staff application for the client journey*

This is a `Flask <https://flask.palletsprojects.com>`_ based app that serves webpages to the `ModoBio <https://modobio.com>`_ staff. The pages contain the intake and data gathering forms for the *client journey*. The `Odyssey <https://en.wikipedia.org/wiki/Odyssey>`_ is of course the most famous journey of all time! 🤓
"""

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


__version__ = '0.0.3'

app = Flask(__name__)
CORS(app)

app.config.from_pyfile('config.py')

print(app.config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

from odyssey.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')
