import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/modobio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from odyssey.views.main import bp
app.register_blueprint(bp)

from odyssey.views.intake import bp
app.register_blueprint(bp, url_prefix='/intake')

from odyssey.views.doctor import bp
app.register_blueprint(bp, url_prefix='/doctor')

from odyssey.views.pt import bp
app.register_blueprint(bp, url_prefix='/pt')
