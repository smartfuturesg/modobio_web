from flask import render_template, Blueprint, session, redirect, request, url_for, flash
from werkzeug.security import check_password_hash

from odyssey import db
from odyssey.forms.main import StaffLoginForm, ClientSearchForm
from odyssey.models.main import Staff
from odyssey.models.client import ClientInfo

bp = Blueprint('main', __name__)

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
        email = request.form['email'].lower()
        staff = Staff.query.filter_by(email=email).one_or_none()

        if staff and check_password_hash(staff.password, request.form['password']):
            session.clear()
            session['staffid'] = staff.staffid
            session['staffname'] = staff.fullname
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

    clients = ClientInfo.query.filter(db.and_(*clauses)).all()
    
    if not clients:
        flash('Client not found, please try again.')
        return render_template('main/clientsearch.html', form=ClientSearchForm())

    return render_template('main/clientselect.html', clients=clients)

@bp.route('/clientload', methods=('POST',))
def clientload():
    clientid = request.form['clientid']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()

    session['clientid'] = clientid
    session['clientname'] = ci.fullname

    return redirect(url_for('.index'))
