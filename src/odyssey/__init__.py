""" A staff application for the Modo Bio client journey.

This is a `Flask <https://flask.palletsprojects.com>`_ based app that serves webpages to the `ModoBio <https://modobio.com>`_ staff. 
The pages contain the intake and data gathering forms for the *client journey*. The `Odyssey <https://en.wikipedia.org/wiki/Odyssey>`_ 
is of course the most famous journey of all time! 🤓
"""
import logging
import os
import time

from bson.binary import UuidRepresentation
from bson.codec_options import CodecOptions, DatetimeConversion
from celery import Celery
from elasticsearch import Elasticsearch
from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_pymongo import PyMongo, ASCENDING, DESCENDING
from flask_sqlalchemy import SQLAlchemy
from pymongo.errors import CollectionInvalid
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import class_mapper
from werkzeug.exceptions import HTTPException

import odyssey.utils.converters

from odyssey.utils.errors import exception_handler, http_exception_handler
from odyssey.utils.logging import JsonFormatter
from odyssey.utils.json import JSONProvider

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

celery = Celery(__name__, broker=conf.broker_url, backend=conf.result_backend)

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

            $ export FLASK_APP=odyssey:create_app()
            $ flask run

        See Also
        --------
        :mod:`odyssey.config` and :mod:`odyssey.defaults`.
    """
    # Temporarily quiet login function
    logging.getLogger(name='odyssey.utils.auth').setLevel(logging.INFO)

    app = Flask(__name__, static_folder="static") 

    # Extended JSON (de)serialization.
    # TODO: not yet ready for primetime. Breaks too many things.
    # app.json = JSONProvider(app)

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

    # Custom path parameter converters
    for converter_class in odyssey.utils.converters.__all__:
        converter = getattr(odyssey.utils.converters, converter_class)
        app.url_map.converters[converter.name] = converter

    # Load the API.
    from odyssey.api import bp, api, bp_v2, api_v2

    # Register error handlers
    #
    # Basic exceptions (unexpected erros) are handled by Flask,
    # HTTP exceptions (expected errors) are handled by Flask-RestX.
    # Flask-RestX does not have a nice register function like Flask does,
    # but this is essentially what the @api.errorhandler decorator does.
    app.register_error_handler(Exception, exception_handler)
    api.error_handlers[HTTPException] = http_exception_handler
    api_v2.error_handlers[HTTPException] = http_exception_handler

    # api._doc or Api(doc=...) is not True/False,
    # it is 'path' (default '/') or False to disable.
    if not app.config['SWAGGER_DOC']:
        api._doc = False
        api_v2._doc = False
    api.version = app.config['VERSION_STRING']
    api_v2.version = app.config['VERSION_STRING']

    # Register development-only endpoints.
    if app.config['DEV']:
        from odyssey.api.misc.postman import ns_dev
        api.add_namespace(ns_dev)

        from odyssey.api.notifications.routes import ns_dev_push, ns_dev_notif
        api.add_namespace(ns_dev_push)
        api.add_namespace(ns_dev_notif)

    
    # Api is registered through a blueprint, Api.init_app() is not needed.
    # https://flask-restx.readthedocs.io/en/latest/scaling.html#use-with-blueprints
    app.register_blueprint(bp)
    app.register_blueprint(bp_v2, url_prefix='/v2')

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
                    search.build_es_indices()
                except ProgrammingError as err:
                    # ProgrammingError wraps lower level errors, in this case a
                    # psycopg2.errors.UndefinedTable error. Ignore UndefinedTable error.
                    if 'UndefinedTable' not in str(err):
                        raise err
    # mongo db
    if app.config['MONGO_URI']:
        mongo.init_app(app)

        # Wearables collection needs non-standard option for
        # timezone-aware datetime and UUID interpretation.
        co = CodecOptions(
            tz_aware=True,
            datetime_conversion=DatetimeConversion.DATETIME,
            uuid_representation=UuidRepresentation.STANDARD)

        try:
            mongo.db.create_collection('wearables', codec_options=co)
        except CollectionInvalid:
            # Already exists
            pass

        # Wearables index, only needs to be created once.
        # Does not fail if already exists.
        mongo.db.wearables.create_index([
            ('user_id', ASCENDING),
            ('wearable', ASCENDING),
            ('date', DESCENDING)],
            name='user_id-wearable-date-index',
            unique=True)

    # Reset login function log level
    logging.getLogger(name='odyssey.utils.auth').setLevel(conf.LOG_LEVEL)

    # Print all config settings to debug, in DEV only.
    if app.config['DEV']:
        logger.debug(conf.dump())

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
    TypeError
        Raised if :attr:`other` is neither a dict nor a :class:`sqlalchemy.Table` instance.

    ValueError
        Raised if :attr:`other` is an instance of a different sqlalchemy model than the
        instance it is trying to update.

    AttributeError
        Raised if key from :attr:`other` as dict does not exist on the model it is trying
        to update.
    """
    if isinstance(other, dict):
        for k, v in other.items():
            # Raises AttributeError if key does not exist on self.
            getattr(self, k)
            setattr(self, k, v)
    else:
        try:
            self_type = class_mapper(type(self))
            other_type = class_mapper(type(other))
        except sqlalchemy.orm.exc.UnmappedClassError:
            raise TypeError(f'{other!r} is not a dict or sqlalchemy model.')

        if self_type != other_type:
            raise ValueError(f'Trying to update an instance of {self_type.class_} '
                            f'with an instance of {other_type.class_}')

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
    app.app_context().push()
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
