import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

__version__ = '0.0.1'

app = Flask(__name__)
app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/modobio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

