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
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import class_mapper
from werkzeug.exceptions import HTTPException

# Temporary fix
from flask.scaffold import _endpoint_from_view_func
import flask.helpers
flask.helpers._endpoint_from_view_func = _endpoint_from_view_func

from odyssey.utils.logging import JsonFormatter
from odyssey.utils.errors import exception_handler, http_exception_handler

from odyssey.config import Config
conf = Config()

# Configure logging before Flask() is called.
if conf.LOG_FORMAT_JSON:
    formatter = JsonFormatter()
else:
    fmt = '%(levelname)-8s - %(asctime)s - %(name)s - %(message)s'
    formatter = logging.Formatter(fmt=fmt)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Root logger
logger = logging.getLogger()
logger.setLevel(conf.LOG_LEVEL)

# Add handler only once, prevent messages from being duplicated.
if not logger.hasHandlers():
    logger.addHandler(handler)

# Some loggers in dependent packages don't get configured with the rest.
# To see a list of all available loggers, uncomment the following lines,
# run `flask run 2> /dev/null`, and add to the list below.
#
# import pprint
# pprint.pprint(logging.root.manager.loggerDict)

for name in ('sqlalchemy', 'flask_cors', 'werkzeug'):
    logging.getLogger(name=name).setLevel(conf.LOG_LEVEL)

log_level_num = logging.getLevelName(conf.LOG_LEVEL)

# SQLAlchemy and elasticsearch are too verbose, fine tune several loggers.
if log_level_num < logging.WARN:
    logging.getLogger('elasticsearch').setLevel(logging.WARN)
    logging.getLogger('sqlalchemy.orm.mapper.Mapper').setLevel(logging.WARN)
    logging.getLogger('sqlalchemy.orm.relationships.RelationshipProperty').setLevel(logging.WARN)
    logging.getLogger('sqlalchemy.orm.strategies.LazyLoader').setLevel(logging.WARN)

if log_level_num < logging.INFO:
    logging.getLogger('sqlalchemy.orm.path_registry').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)

    # **WARNING**: sqlalchemy.engine.Engine at DEBUG level logs every row
    # stored in/fetched from DB, including password hashes. Don't ever do that.
    # If you must see what's going on while developing, comment this out.
    # Otherwise, keep this at INFO level.
    logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.INFO)

# Instantiate Flask extensions.
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
ma = Marshmallow()
mongo = PyMongo()

celery = Celery(__name__, broker=Config().broker_url, backend=Config().result_backend)

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

    # Load configuration.
    app.config.from_object(conf)

    # Initialize all extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    ma.init_app(app)

    celery.conf.update(app.config)

    # Convenience function
    db.Model.update = _update

    # Load the API.
    from odyssey.api import bp, api

    # Register error handlers
    #
    # Basic exceptions (unexpected erros) are handled by Flask,
    # HTTP exceptions (expected errors) are handled by Flask-RestX.
    # Flask-RestX does not have a nice register function like Flask does,
    # but this is essentially what the @api.errorhandler decorator does.
    app.register_error_handler(Exception, exception_handler)
    api.error_handlers[HTTPException] = http_exception_handler

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

        from odyssey.api.payment.routes import ns_dev
        api.add_namespace(ns_dev)

    # Api is registered through a blueprint, Api.init_app() is not needed.
    # https://flask-restx.readthedocs.io/en/latest/scaling.html#use-with-blueprints
    app.register_blueprint(bp)

    # Elasticsearch setup.
    app.elasticsearch = None
    if app.config['ELASTICSEARCH_URL']:
        app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        if not app.config['TESTING']:
            with app.app_context():
                # action.destructive_requires_namesetting defaults to true in v8,
                # which disallows use of wildcards or _all.
                app.elasticsearch.indices.delete(index='clients,staff', ignore_unavailable=True)
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


# TODO: this should be moved to utils/base/models.py once all models derive
# from our custom base model.
def _update(self, other):
    """ Update a table instance.

    Update a table instance with values from a dict or another instance
    of the same table class. Values not present in :attr:`other` are not
    updated.

    Parameters
    ----------
    other : dict or :class:`sqlalchemy.Table` instance
        The dict or table instance providing the values to be updated.

    Raises
    ------
    :class:`sqlalchemy.orm.exc.UnmappedClassError`
        Raised if :attr:`other` is neither a dict nor a :class:`sqlalchemy.Table` instance.
    """
    if isinstance(other, dict):
        for k, v in other.items():
            setattr(self, k, v)
    else:
        # This raises UnmappedClassError if other is not a table instance.
        # Don't catch error, but let if fail.
        class_mapper(type(other))
        for k, v in other.__dict__.items():
            if k.startswith('_sa'):
                continue
            setattr(self, k, v)

def init_celery(app=None):
    """
    Function to prepare a celery instance. Requires the flask app instance

    This is called from both create_app and celery_app 
    """

    app = app or create_app()

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
