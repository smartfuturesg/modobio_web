import datetime

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, FloatField, HiddenField, RadioField, StringField, SelectField

from odyssey.constants import COUNTRIES, GENDERS, USSTATES, CONTACT_METHODS, YESNO, BOOLIFY

today = datetime.date.today()
next_year = datetime.date(year=today.year + 1, month=today.month, day=today.day)

class ClientInfoForm(FlaskForm):
    firstname = StringField('First name')
    middlename = StringField('Middle name(s)')
    lastname = StringField('Last name')
    s1 = HiddenField(id='spacer')

    guardianname = StringField('Parent or guardian name (if applicable)')
    guardianrole = StringField('Parent or guardian relationship')

    s2 = HiddenField(id='spacer')
    street = StringField('Address')
    city = StringField('City')
    state = SelectField('State', choices=USSTATES, default='AZ')
    zipcode = StringField('Zip')
    country = SelectField('Country', choices=COUNTRIES, default='US')

    s3 = HiddenField(id='spacer')
    email = StringField('Email address') 
    phone = StringField('Phone')
    preferred = SelectField('Preferred method of contact', choices=CONTACT_METHODS)

    s4 = HiddenField(id='spacer')
    ringsize = FloatField('Ringsize for Oura Ring')

    s5 = HiddenField(id='spacer')
    emergency_contact = StringField('Emergency contact name')
    emergency_phone = StringField('Emergency contact phone')

    s6 = HiddenField(id='spacer')
    healthcare_contact = StringField('Primary healthcare provider name')
    healthcare_phone = StringField('Primary healthcare provider phone')

    s7 = HiddenField(id='spacer')
    gender = SelectField('Gender', choices=GENDERS)
    dob = DateField('Date of birth')
    profession = StringField('Profession or occupation')


class ClientSignForm(FlaskForm):
    fullname = StringField('Full name')
    guardianname = StringField('Parent or guardian name (if applicable)')
    signdate = DateField('Date', default=today)
    signature = HiddenField()


class ClientConsentForm(ClientSignForm):
    infectious_disease = RadioField(choices=YESNO, coerce=BOOLIFY)


class ClientReleaseForm(ClientSignForm):
    release_by_other = StringField()
    release_to_other = StringField()
    release_of_all = RadioField(choices=((1, 'all'), (0, 'other')),
                        coerce=BOOLIFY,
                        default=1)
    release_of_other = StringField()
    release_date_from = DateField()
    release_date_to = DateField()
    release_purpose = StringField()

    emergency_contact = StringField('Emergency contact name')
    emergency_phone = StringField('Emergency contact phone')

    dob = DateField('Date of birth')
    address = StringField('Address')
    phone = StringField('Phone', render_kw={'type': 'phone'})
    email = StringField('Email', render_kw={'type': 'email'})


class ClientReceiveForm(FlaskForm):
    receive_docs = BooleanField(default='checked')


class ClientIndividualContractForm(ClientSignForm):
    doctor_consult = BooleanField()
    pt_consult = BooleanField()
    data_monitoring = BooleanField()
    drinks = BooleanField()
