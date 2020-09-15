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

from odyssey.config import Config

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
ma = Marshmallow()

def create_app(flask_dev=None):
    """ Initialize an instance of the Flask app.

        This function is an 'app factory'. It creates an instance of :class:`flask.Flask`.
        It is the main function to call to get the program started.

        Parameters
        ----------
        flask_dev : str
            Sets the development environment, which determines a range of configuration
            options that will be used. See :mod:`odyssey.config` for more information.

        Returns
        -------
        An instance of :class:`flask.Flask`, with approrpiate configuration.

        Examples
        --------
        Running the flask builtin test server from the command line:

        .. code-block:: shell

            $ export FLASK_ENV=development
            $ export FLASK_APP=odyssey:create_app("local")
            $ flask run

        Running as a uWSGI program:

        .. code-block:: ini

            [uwsgi]
            plugins = python
            pythonpath = <path-to-installation>
            wsgi-file = <path-to-installation>/odyssey/__init__.py
            callable = create_app(flask_dev='local')
            env = FLASK_ENV=development

        See Also
        --------
        odyssey.config
    """
    app = Flask(__name__)

    app.config.from_object(Config(flask_dev=flask_dev))
    app.config['APPLICATION_ROOT'] = '/api'

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    ma.init_app(app)

    db.Model.update = _update

    from odyssey.api import bp, api
    app.register_blueprint(bp)
    api.version = app.config['VERSION']

    from odyssey.api.errors import register_handlers
    register_handlers(app)

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
