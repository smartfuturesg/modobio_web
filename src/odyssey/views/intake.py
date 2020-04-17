import datetime

from flask import render_template, Blueprint, session, redirect, request, url_for
from flask_wtf import FlaskForm
from flask_weasyprint import HTML, render_pdf
from wtforms import BooleanField, DateField, HiddenField, RadioField, StringField, SelectField

from odyssey import db
from odyssey.models import ClientInfo, ClientConsent
from odyssey.constants import COUNTRIES, GENDERS, USSTATES, CONTACT_METHODS, YESNO, BOOLIFY

bp = Blueprint('intake', __name__)

class ClientInfoForm(FlaskForm):
    firstname = StringField('First name')
    middlename = StringField('Middle name(s)')
    lastname = StringField('Last name')
    s1 = HiddenField(id='spacer')

    guardianname = StringField('Parent or guardian name')
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
    emergency_contact = StringField('Emergency contact name')
    emergency_phone = StringField('Emergency contact phone')

    s5 = HiddenField(id='spacer')
    healthcare_contact = StringField('Primary healthcare provider name')
    healthcare_phone = StringField('Primary healthcare provider phone')

    s6 = HiddenField(id='spacer')
    gender = SelectField('Gender', choices=GENDERS)
    dob = DateField('Date of birth')


class ClientConsultContractForm(FlaskForm):
    signature = HiddenField()
    fullname = StringField('Full name')
    guardianname = StringField('Parent or guardian name')
    signdate = DateField('Date', default=datetime.date.today())


class ClientConsentForm(FlaskForm):
    infectious_disease = RadioField('', choices=YESNO, coerce=BOOLIFY)
    signature = HiddenField()
    fullname = StringField('Full name')
    guardianname = StringField('Parent or guardian name')
    signdate = DateField('Date', default=datetime.date.today())


class ClientReleaseForm(FlaskForm):
    fullname = StringField('Full name')
    dob = DateField('Date of birth')
    address = StringField('Address')
    phone = StringField('Phone', render_kw={'type': 'phone'})
    email = StringField('Email', render_kw={'type': 'email'})

    release_to_emergency_contact = BooleanField('')
    release_to_primary_care_contact = BooleanField('')
    release_of_all = RadioField('', choices=((1, 'all'), (0, 'other')), coerce=BOOLIFY)
    release_of_other = StringField('other')

    signature = HiddenField()
    guardianname = StringField('Parent or guardian name')
    signdate = DateField('Date', default=datetime.date.today())


class ClientFinancialForm(FlaskForm):
    signature = HiddenField()
    fullname = StringField('Full name')
    guardianname = StringField('Parent or guardian name')
    signdate = DateField('Date', default=datetime.date.today())


class ClientReceiveForm(FlaskForm):
    receive_docs = BooleanField('', default='checked')


class ClientSubscriptionContractForm(FlaskForm):
    signature = HiddenField()
    fullname = StringField('Full name')
    guardianname = StringField('Parent or guardian name')
    signdate = DateField('Date', default=datetime.date.today())


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
        session['clientname'] = f'{ci.firstname} {ci.lastname}'

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
    clientid = session.get('clientid')
    cc = ClientConsent.query.filter_by(clientid=clientid).one_or_none()

    form = ClientConsentForm(obj=cc)

    if request.method == 'GET':
        return render_template('intake/consent.html', form=form)

    if not cc:
        cc = ClientConsent(**dict(request.form), clientid=clientid)
        db.session.add(cc)
    else:
        form.populate_obj(cc)
    db.session.commit()

    html = render_template('intake/consent.html', form=form, pdf=True)
    # TODO: this needs to be saved somewhere
    # return render_pdf(HTML(string=html))
    return redirect(url_for('.release'))

@bp.route('/release', methods=('GET', 'POST'))
def release():
    clientid = session['clientid']
    fullname = session['clientname']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    address = f'{ci.street}, {ci.city}, {ci.state}, {ci.zipcode}'
    form = ClientReleaseForm(obj=ci, fullname=fullname, address=address)

    if request.method == 'GET':
        return render_template('intake/release.html', form=form)

    html = render_template('intake/release.html', form=form, pdf=True)
    # TODO: store pdf
    # return render_pdf(HTML(string=html))
    return redirect(url_for('.financial'))

@bp.route('/financial', methods=('GET', 'POST'))
def financial():
    clientid = session['clientid']
    fullname = session['clientname']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    form = ClientFinancialForm(obj=ci, fullname=fullname)

    if request.method == 'GET':
        return render_template('intake/financial.html', form=form)

    html = render_template('intake/financial.html', form=form, pdf=True)
    # TODO: store pdf
    # return render_pdf(HTML(string=html))
    return redirect(url_for('.send'))

@bp.route('/send', methods=('GET', 'POST'))
def send():
    if request.method == 'GET':
        return render_template('intake/send.html', form=ClientReceiveForm())
    return redirect(url_for('main.index'))

@bp.route('/consult', methods=('GET', 'POST'))
def consult():
    clientid = session['clientid']
    fullname = session['clientname']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    form = ClientConsultContractForm(obj=ci, fullname=fullname)

    if request.method == 'GET':
        return render_template('intake/consult.html', form=form)

    html = render_template('intake/consult.html', form=form, pdf=True)
    # TODO: store pdf
    # return render_pdf(HTML(string=html))
    return redirect(url_for('main.index'))

@bp.route('/subscription', methods=('GET', 'POST'))
def subscription():
    clientid = session['clientid']
    fullname = session['clientname']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    form = ClientSubscriptionContractForm(obj=ci, fullname=fullname)

    if request.method == 'GET':
        return render_template('intake/subscription.html', form=form)

    html = render_template('intake/subscription.html', form=form, pdf=True)
    # TODO: store pdf
    # return render_pdf(HTML(string=html))
    return redirect(url_for('main.index'))
