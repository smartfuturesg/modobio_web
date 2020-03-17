from flask import render_template, Blueprint, session, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SelectField, SubmitField
from wtforms.validators import Email, InputRequired, NumberRange

from odyssey.intake import db
from odyssey.intake.models import ClientInfo
from odyssey.intake.constants import COUNTRIES, GENDERS, USSTATES

bp = Blueprint('index', __name__)

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

    gender = SelectField('Gender', choices=GENDERS)
    dob = DateField('Date of birth')

    submit = SubmitField('Next')


@bp.route('/clientinfo', methods=['GET', 'POST'])
def clientinfo():
    """ Render a HTML page that asks for basic client info. """
    form = ClientInfoForm()
    if request.method =='GET':
        return render_template('clientinfo.html', form=form)

    f = dict(request.form)
    f.pop('submit')
    ci = ClientInfo(**f)

    db.session.add(ci)
    db.session.commit()
    return 'Reroute to next page'
