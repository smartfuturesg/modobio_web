""" A staff application for the Modo Bio client journey.

This is a `Flask <https://flask.palletsprojects.com>`_ based app that serves webpages to the `ModoBio <https://modobio.com>`_ staff. 
The pages contain the intake and data gathering forms for the *client journey*. The `Odyssey <https://en.wikipedia.org/wiki/Odyssey>`_ 
is of course the most famous journey of all time! 🤓
"""
import logging
import os
import time

from celery import Celery
from elasticsearch import Elasticsearch
from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_pymongo import PyMongo 
from flask_sqlalchemy import SQLAlchemy
from pythonjsonlogger import jsonlogger
from sqlalchemy.exc import ProgrammingError

# Temporary fix
from flask.scaffold import _endpoint_from_view_func
import flask.helpers
flask.helpers._endpoint_from_view_func = _endpoint_from_view_func

from odyssey.config import Config
conf = Config()

# Logging configuration, before Flask() is called.
def _audit(msg, *args, **kwargs):
    """
    Log a message with severity 'AUDIT' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    logging.log(25, msg, *args, **kwargs)

logging.Logger.audit = _audit
logging.Formatter.converter = time.gmtime
logging.Formatter.default_msec_format = '%s.%03dZ'
logging.addLevelName(25, 'AUDIT')
logging.captureWarnings(True)

if conf.LOG_FORMAT_JSON:
    formatter = jsonlogger.JsonFormatter()
else:
    fmt = '%(levelname)-8s %(asctime)s - %(name)s - %(message)s'
    formatter = logging.Formatter(fmt=fmt)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

# None is for the root logger
for name in (None, 'sqlalchemy', 'flask_cors', 'werkzeug'):
    logger = logging.getLogger(name=name)
    logger.addHandler(handler)
    logger.setLevel(conf.LOG_LEVEL)

# SQLAlchemy is too verbose, turn down Mapper logger
logging.getLogger('sqlalchemy.orm.mapper.Mapper').setLevel(logging.WARNING)

# Some loggers in  dependent packages don't get configured with the rest.
# To see a list of all loggers, uncomment the following lines and run `flask run 2> /dev/null`
#
# import pprint
# pprint.pprint(logging.root.manager.loggerDict)

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
ma = Marshmallow()
celery = Celery()
mongo = PyMongo()

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
            $ export FLASK_APP=odyssey:create_app()
            $ flask run

        See Also
        --------
        :mod:`odyssey.config` and :mod:`odyssey.defaults`.
    """
    app = Flask(__name__, static_folder="static") 


    from flask.logging import default_handler
    app.logger.removeHandler(default_handler)

    # Load configuration.
    app.config.from_object(conf)

    # Initialize all extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    ma.init_app(app)
    init_celery(app)

    # Convenience function
    db.Model.update = _update

    # Load the API.
    from odyssey.api import bp, api

    # api._doc or Api(doc=...) is not True/False,
    # it is 'path' (default '/') or False to disable.
    if not app.config['SWAGGER_DOC']:
        api._doc = False
    api.version = app.config['API_VERSION']

    # Register development-only endpoints.
    if app.config['DEV']:
        from odyssey.api.misc.postman import ns_dev
        api.add_namespace(ns_dev)

        from odyssey.api.notifications.routes import ns_dev
        api.add_namespace(ns_dev)

    # Api is registered through a blueprint, Api.init_app() is not needed.
    # https://flask-restx.readthedocs.io/en/latest/scaling.html#use-with-blueprints
    app.register_blueprint(bp)

    from odyssey.utils.errors import register_handlers
    register_handlers(app)
    
    # Elasticsearch setup.
    app.elasticsearch = None
    if app.config['ELASTICSEARCH_URL']:
        app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        if not app.config['TESTING']:
            with app.app_context():
                app.elasticsearch.indices.delete('_all')
                from odyssey.utils import search
                try:
                    search.build_ES_indices()
                except ProgrammingError as err:
                    # ProgrammingError wraps lower level errors, in this case a
                    # psycopg2.errors.UndefinedTable error. Ignore UndefinedTable error.
                    if 'UndefinedTable' not in str(err):
                        raise err
    # mongo db
    if app.config['MONGO_URI']:
        mongo.init_app(app)

    return app


# Custom method to easily update db table from a dict
def _update(self, form: dict):
    for k, v in form.items():
        setattr(self, k, v)


def init_celery(app=None):
    """
    Function to prepare a celery instance. Requires the flask app instance

    This is called from both create_app and celery_app 
    """

    app = app or create_app()
    celery.config_from_object(Config())

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
