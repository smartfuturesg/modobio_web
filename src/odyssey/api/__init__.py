from flask import Blueprint

bp = Blueprint('api', __name__)

from odyssey.api import clients, doctor, pt, staff, errors, tokens

