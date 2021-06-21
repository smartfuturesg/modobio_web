""" A staff application for the Modo Bio client journey.

This is a `Flask <https://flask.palletsprojects.com>`_ based app that serves webpages to the `ModoBio <https://modobio.com>`_ staff. 
The pages contain the intake and data gathering forms for the *client journey*. The `Odyssey <https://en.wikipedia.org/wiki/Odyssey>`_ 
is of course the most famous journey of all time! 🤓
"""
import os

from celery import Celery
from elasticsearch import Elasticsearch
from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

# Temporary fix
from flask.scaffold import _endpoint_from_view_func
import flask.helpers
flask.helpers._endpoint_from_view_func = _endpoint_from_view_func

from odyssey.config import Config

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
ma = Marshmallow()
celery = Celery()

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
    app = Flask(__name__, static_folder="static") 

    app.config.from_object(Config())
    app.config['APPLICATION_ROOT'] = '/api'

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    ma.init_app(app)
    db.Model.update = _update
    init_celery(app)
    from odyssey.api import bp, api

    # api._doc or Api(doc=...) is not True/False,
    # it is 'path' (default '/') or False to disable.
    if not app.config['SWAGGER_DOC']:
        api._doc = False
    api.version = app.config['VERSION']

    # api and bp are connected, register after changing settings.
    app.register_blueprint(bp)

    from odyssey.utils.errors import register_handlers
    register_handlers(app)

    # Unprotected route, only relevant to developers
    if app.config['LOCAL_CONFIG']:
        from odyssey.api.misc.postman import bp
        app.register_blueprint(bp, url_prefix='/postman')
    
    #Elasticsearch config if ELASTICSEARCH_URL was set as an env variable
    #Otherwise it will be none and search won't work.
    if app.config['ELASTICSEARCH_URL']:
        app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        if not app.config['TESTING']:
            with app.app_context():
                app.elasticsearch.indices.delete('_all')
                from odyssey.utils import search
                try:
                    search.build_ES_indices()
                except exc.ProgrammingError as e:
                    if not e._message.__str__().__contains__('UndefinedTable'):
                        raise e
    else:
        app.elasticsearch = None


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
