import datetime

from flask import render_template, Blueprint, session, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import DateField, RadioField, StringField, SelectField, SubmitField
from wtforms.validators import Email, InputRequired, NumberRange

from odyssey.intake import db
from odyssey.intake.models import ClientInfo, HealthcareConsent
from odyssey.constants import COUNTRIES, GENDERS, USSTATES, CONTACT_METHODS

bp = Blueprint('intake', __name__)

class ClientInfoForm(FlaskForm):
    firstname = StringField('First name')
    middlename = StringField('Middle name(s)')
    lastname = StringField('Last name')

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
    dob = DateField('Date of birth')


class HealthcareConsentForm(FlaskForm):
    infectious_disease = RadioField('Infectious disease', choices=((False, 'No'), (True, 'Yes')))
    fullname = StringField('Full name')
    signature = StringField('Signature')
    signdate = DateField('Date', default=datetime.date.today())


@bp.route('/clientinfo', methods=['GET', 'POST'])
def clientinfo():
    """ Render a HTML page that asks for basic client info. """
    if request.method =='GET':
        return render_template('clientinfo.html', form=ClientInfoForm())

    ci = ClientInfo(**dict(request.form))

    db.session.add(ci)
    db.session.commit()
    return redirect(url_for('intake.healthcare_consent'))

@bp.route('/healthcare_consent', methods=['GET', 'POST'])
def healthcare_consent():
    """ DOC """
    if request.method == 'GET':
        return render_template('healthcare_consent.html', form=HealthcareConsentForm())

    hcc = HealthcareConsent(**dict(request.form))

    db.session.add(hcc)
    db.session.commit()
    return 'Reroute to next page'