from flask import render_template, Blueprint, session, redirect, request, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from werkzeug.security import check_password_hash

from odyssey import db
from odyssey.models import Staff, ClientInfo

bp = Blueprint('main', __name__)

class StaffLoginForm(FlaskForm):
    email = StringField('Email', render_kw={'type': 'email'})
    password = PasswordField('Password')


class ClientSearchForm(FlaskForm):
    firstname = StringField('First name')
    lastname = StringField('Last name')
    email = StringField('Email address', render_kw={'type': 'email'})
    phone = StringField('Phone number', render_kw={'type': 'phone'})


@bp.route('/')
def index():
    if not session.get('staffid'):
        return redirect(url_for('.login'))

    if not session.get('clientid'):
        return redirect(url_for('.clientsearch'))

    return render_template('main/index.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        staff = Staff.query.filter_by(email=email).first()

        if staff and check_password_hash(staff.password, password):
            session.clear()
            session['staffid'] = staff.staffid
            session['staffname'] = f'{staff.firstname} {staff.lastname}'
            return redirect(url_for('.index'))

        flash('Incorrect email or password')

    return render_template('main/login.html', form=StaffLoginForm())

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('.index'))

@bp.route('/clientsearch', methods=('GET', 'POST'))
def clientsearch():
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
def clientload():
    clientid = request.form['clientid']
    ci = db.session.query(ClientInfo).filter_by(clientid=clientid).one()
    fullname = f'{ci.firstname} {ci.lastname}'

    session['clientid'] = clientid
    session['clientname'] = fullname

    return redirect(url_for('.index'))
