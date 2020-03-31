from flask import render_template, Blueprint, session, redirect, request, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from werkzeug.security import check_password_hash

from odyssey import db
from odyssey.main.models import Employees
from odyssey.intake.models import ClientInfo

bp = Blueprint('main', __name__)

class EmployeeLoginForm(FlaskForm):
    email = StringField('Email', render_kw={'type': 'email'})
    password = PasswordField('Password')


class ClientSearchForm(FlaskForm):
    firstname = StringField('First name')
    lastname = StringField('Last name')
    email = StringField('Email address', render_kw={'type': 'email'})
    phone = StringField('Phone number', render_kw={'type': 'phone'})


@bp.route('/')
def index():
    if not session.get('employee_id'):
        return redirect(url_for('.login'))

    if not session.get('clientid'):
        return redirect(url_for('.client_search'))

    return render_template('main/index.html')


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
            return redirect(url_for('.index'))

        flash('Incorrect email or password')

    return render_template('main/login.html', form=EmployeeLoginForm())

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('.index'))

@bp.route('/clientsearch', methods=('GET', 'POST'))
def client_search():
    if request.method == 'GET':
        return render_template('main/clientsearch.html', form=ClientSearchForm())

    clauses = []
    if request.form['firstname']:
        clauses.append(ClientInfo.firstname.ilike(f'%{request.form["firstname"]}%'))
    if request.form['lastname']:
        clauses.append(ClientInfo.lastname.ilike(f'%{request.form["lastname"]}%'))
    if request.form['phone']:
        clauses.append(ClientInfo.phone.ilike(f'%{request.form["phone"]}%'))
    if request.form['email']:
        clauses.append(ClientInfo.email.ilike(f'%{request.form["email"]}%'))

    clients = db.session.query(ClientInfo).filter(db.and_(*clauses)).all()
    
    if not clients:
        flash('Client not found, please try again.')
        return render_template('main/clientsearch.html', form=ClientSearchForm())

    return render_template('main/clientselect.html', clients=clients)


@bp.route('/clientload', methods=('POST',))
def client_load():
    session['clientid'] = request.form['clientid']
    session['client_name'] = request.form['client_name']
    return redirect(url_for('.index'))
