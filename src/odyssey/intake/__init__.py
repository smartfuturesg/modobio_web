# This should all be moved to a main file to run all sub-flasks at once.
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/modobio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from .views import *
app.register_blueprint(bp)
# app.add_url_rule('/intake', endpoint='index')
