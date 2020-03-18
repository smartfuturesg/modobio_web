from flask import render_template, Blueprint, session, redirect, request, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from werkzeug.security import check_password_hash

from odyssey import db
from odyssey.main.models import Employees

bp = Blueprint('main', __name__)

class EmployeeLoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Password')


@bp.route('/')
def index():
    employee_id = session.get('employee_id')
    if not employee_id:
        return redirect(url_for('main.login'))

    return redirect(url_for('intake.clientinfo'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        emp_email = request.form['email']
        emp_pass = request.form['password']
        emp = Employees.query.filter_by(email=emp_email).first()

        if emp and check_password_hash(emp.password, emp_pass):
            session.clear()
            session['employee_id'] = emp.employee_id
            session['employee_name'] = f'{emp.firstname} {emp.lastname}'
            return redirect(url_for('main.index'))

        flash('Incorrect email or password')

    return render_template('login.html', form=EmployeeLoginForm())
