from flask import Blueprint
from flask_restx import Api

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Token Authorization'
    },
    'Basic Auth': {
        'type': 'basic',
        'in': 'header',
        'name': 'Basic Authorization'
    },
}

bp = Blueprint('api', __name__)
api = Api(bp, authorizations=authorizations)

from odyssey.api import (
    clients,
    doctor,
    errors,
    pt,
    remote_clients,
    staff,
    tokens,
    trainer,
    wearables
)
