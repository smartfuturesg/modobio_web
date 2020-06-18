from flask import Blueprint
from flask_restx import Api

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

bp = Blueprint('api', __name__)
api = Api(bp, authorizations=authorizations)

from odyssey.api import clients, doctor, pt, staff, errors, tokens



