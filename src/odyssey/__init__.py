import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/modobio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from odyssey.main.views import bp
app.register_blueprint(bp)

from odyssey.intake.views import bp
app.register_blueprint(bp)

from odyssey.doctor.views import bp
app.register_blueprint(bp)

from odyssey.physical_therapist.views import bp
app.register_blueprint(bp)
