from flask import Blueprint
from odyssey.doctor import routes, models

doctor_bp = Blueprint('doctor_bp', __name__)

