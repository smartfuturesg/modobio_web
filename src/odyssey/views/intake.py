import datetime

from flask import render_template, Blueprint, session, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, HiddenField, RadioField, StringField, SelectField

from odyssey import db
from odyssey.models import ClientInfo, ClientConsent
from odyssey.constants import COUNTRIES, GENDERS, USSTATES, CONTACT_METHODS

bp = Blueprint('intake', __name__)

class ClientInfoForm(FlaskForm):
    firstname = StringField('First name')
    middlename = StringField('Middle name(s)')
    lastname = StringField('Last name')

    guardianname = StringField('Parent or guardian name')
    guardianrole = StringField('Parent or guardian relationship')

    street = StringField('Address')
    city = StringField('City')
    state = SelectField('State', choices=USSTATES, default='AZ')
    zipcode = StringField('Zip')
    country = SelectField('Country', choices=COUNTRIES, default='US')

    email = StringField('Email address') 
    phone = StringField('Phone')
    preferred = SelectField('Preferred method of contact', choices=CONTACT_METHODS)

    emergency_contact = StringField('Emergency contact name')
    emergency_phone = StringField('Emergency contact phone')

    healthcare_contact = StringField('Primary healthcare provider name')
    healthcare_phone = StringField('Primary healthcare provider phone')

    gender = SelectField('Gender', choices=GENDERS)
    dob = DateField('Date of birth', render_kw={'type': 'date'})


class ClientConsultContractForm(FlaskForm):
    signature = HiddenField()
    fullname = StringField('Full name')
    signdate = DateField('Date', default=datetime.date.today(), render_kw={'type': 'date'})


class ClientConsentForm(FlaskForm):
    infectious_disease = RadioField('Infectious disease',
                                    choices=((0, 'No'), (1, 'Yes')))
    signature = HiddenField()
    fullname = StringField('Full name')
    signdate = DateField('Date', default=datetime.date.today(), render_kw={'type': 'date'})


class ClientReleaseForm(FlaskForm):
    fullname = StringField('Full name')
    dob = DateField('Date of birth', render_kw={'type': 'date'})
    address = StringField('Address')
    phone = StringField('Phone', render_kw={'type': 'phone'})
    email = StringField('Email', render_kw={'type': 'email'})

    release_to_emergency_contact = BooleanField('Emergency contact')
    release_to_primary_care_contact = BooleanField('Primary care contact')
    release_of_all = RadioField('', choices=(('all', 'all'), ('other', 'other')))
    release_of_other = StringField('other')

    signature = HiddenField()
    signdate = DateField('Date', default=datetime.date.today(), render_kw={'type': 'date'})


class CientFinancialForm(FlaskForm):
    signature = HiddenField()
    fullname = StringField('Full name')
    signdate = DateField('Date', default=datetime.date.today(), render_kw={'type': 'date'})


class ClientReceiveForm(FlaskForm):
    receive_docs = BooleanField('', default='checked')


class ClientSubscriptionContractForm(FlaskForm):
    signature = HiddenField()
    fullname = StringField('Full name')
    signdate = DateField('Date', default=datetime.date.today(), render_kw={'type': 'date'})


@bp.route('/clientinfo', methods=['GET', 'POST'])
def clientinfo():
    """ Render a HTML page that asks for basic client info. """
    clientid = session.get('clientid')

    if not clientid:
        if request.method =='GET':
            return render_template('intake/clientinfo.html', form=ClientInfoForm())

        ci = ClientInfo(**dict(request.form))
        db.session.add(ci)
        db.session.commit()

        session['clientid'] = ci.clientid
        session['client_name'] = f'{ci.firstname} {ci.lastname}'

        return redirect(url_for('.consent'))

    else:
        ci = ClientInfo.query.filter_by(clientid=clientid).one()
        form = ClientInfoForm(obj=ci)

        if request.method =='GET':
            return render_template('intake/clientinfo.html', form=form)

        form.populate_obj(ci)
        db.session.commit()

        return redirect(url_for('.consent'))

@bp.route('/consent', methods=('GET', 'POST'))
def consent():
    """ DOC """
    if request.method == 'GET':
        return render_template('intake/consent.html', form=ClientConsentForm())

    form = dict(request.form)
    # Coercing did not work
    ifd = form.get('infectious_disease')
    if ifd != None:
        form['infectious_disease'] = bool(int(ifd))
    form['clientid'] = session['clientid']
    hcc = ClientConsent(**form)

    db.session.add(hcc)
    db.session.commit()
    return redirect(url_for('.release'))

@bp.route('/release', methods=('GET', 'POST'))
def release():
    """ DOC """
    clientid = session['clientid']
    fullname = session['client_name']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    address = f'{ci.street}, {ci.city}, {ci.state}, {ci.zipcode}'
    form = ClientReleaseForm(obj=ci, fullname=fullname, address=address)

    if request.method == 'GET':
        return render_template('intake/release.html', form=form)
    return redirect(url_for('.financial'))

@bp.route('/financial', methods=('GET', 'POST'))
def financial():
    """ DOC """
    if request.method == 'GET':
        return render_template('intake/financial.html', form=CientFinancialForm())
    return redirect(url_for('.send'))

@bp.route('/send', methods=('GET', 'POST'))
def send():
    """ DOC """
    if request.method == 'GET':
        return render_template('intake/send.html', form=ClientReceiveForm())
    return redirect(url_for('main.index'))

@bp.route('/consult', methods=('GET', 'POST'))
def consult():
    """ DOC """
    if request.method == 'GET':
        return render_template('intake/consult.html', form=ClientConsultContractForm())
    return redirect(url_for('main.index'))

@bp.route('/subscription', methods=('GET', 'POST'))
def subscription():
    """ DOC """
    if request.method == 'GET':
        return render_template('intake/subscription.html', form=ClientSubscriptionContractForm())
    return redirect(url_for('main.index'))
