from flask import Blueprint
from flask_restplus import Api

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

bp = Blueprint('api', __name__)
api = Api(bp, authorizations=authorizations)

from odyssey.api import clients, errors, tokens

