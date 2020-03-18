from flask import render_template, Blueprint, session, redirect, request, url_for

from odyssey import db

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    employee_id = session.get('employee_id')
    if not employee_id:
        return render_template('index.html')

