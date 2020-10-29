""" A staff application for the Modo Bio client journey.

This is a `Flask <https://flask.palletsprojects.com>`_ based app that serves webpages to the `ModoBio <https://modobio.com>`_ staff. The pages contain the intake and data gathering forms for the *client journey*. The `Odyssey <https://en.wikipedia.org/wiki/Odyssey>`_ is of course the most famous journey of all time! 🤓
"""
import os
import tempfile

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_whooshee import Whooshee

from odyssey.config import Config

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
ma = Marshmallow()
whooshee = Whooshee()

def create_app():
    """ Initialize an instance of the Flask app.

        This function is an 'app factory'. It creates an instance of :class:`flask.Flask`.
        It is the main function to call to get the program started.

        Returns
        -------
        An instance of :class:`flask.Flask`, with appropriate configuration.

        Examples
        --------
        Running the flask builtin test server from the command line:

        .. code-block:: shell

            $ export FLASK_ENV=development
            $ export FLASK_DEV=local
            $ export FLASK_APP=odyssey:create_app()
            $ flask run

        See Also
        --------
        odyssey.config and odyssey.defaults
    """
    app = Flask(__name__)

    app.config.from_object(Config())
    app.config['APPLICATION_ROOT'] = '/api'

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    ma.init_app(app)
    whooshee.init_app(app)

    db.Model.update = _update

    ###Blueprint imports and registration
    
    from odyssey.api import bp, api
    # api._doc or Api(doc=...) is not True/False,
    # it is 'path' (default '/') or False to disable.
    if not app.config['SWAGGER_DOC']:
        api._doc = False
    api.version = app.config['VERSION']
    # api and bp are connected, register after changing settings.
    app.register_blueprint(bp)

    from odyssey.client import client_bp
    app.register_blueprint(client_bp)

    from odyssey.remoteclient import r_client_bp
    app.register_blueprint(r_client_bp)

    from odyssey.doctor import doctor_bp
    app.register_blueprint(doctor_bp)

    from odyssey.pt import pt_bp
    app.register_blueprint(pt_bp)

    from odyssey.registeredfacility import reg_facility_bp
    app.register_blueprint(reg_facility_bp)

    from odyssey.staff import staff_bp
    app.register_blueprint(staff_bp)

    from odyssey.tokens import tokens_bp
    app.register_blueprint(tokens_bp)

    from odyssey.trainer import trainer_bp
    app.register_blueprint(trainer_bp)

    from odyssey.wearables import wearables_bp
    app.register_blueprint(wearables_bp)

    from odyssey.errors.handlers import register_handlers
    register_handlers(app)

    # Unprotected route, only relevant to developers
    if app.config['LOCAL_CONFIG']:
        from odyssey.postman.routes import bp
        app.register_blueprint(bp, url_prefix='/postman')

    # If you want to add another field to search for in the database by whooshee
    # Example: @whooshee.register_model('firstname')
    # Add in lastname
    # @whooshee.register_model('firstname','lastname')
    # YOU MUST DELETE THE whooshee folder! Same level as src, tests, migrations, etc
    with app.app_context():
        try:
            whooshee.reindex()
        except:
            pass

    return app


# Custom method to easily update db table from a dict
def _update(self, form: dict):
    for k, v in form.items():
        setattr(self, k, v)

# Override wtforms.DateTimeField so that it outputs <input type="date"> by default.
import wtforms
class DateInput(wtforms.widgets.Input):
    input_type = 'date'

import odyssey.models
