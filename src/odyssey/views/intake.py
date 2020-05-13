from flask import render_template, Blueprint, session, redirect, request, url_for
from flask_weasyprint import HTML, render_pdf

from odyssey import db
from odyssey.forms.intake import ClientInfoForm, ClientConsentForm, ClientReleaseForm, \
                                 ClientSignForm, ClientReceiveForm, \
                                 ClientIndividualContractForm
from odyssey.models.intake import ClientInfo, ClientConsent, ClientRelease, ClientPolicies, \
                                  ClientConsultContract, ClientSubscriptionContract, \
                                  ClientIndividualContract

bp = Blueprint('intake', __name__)

@bp.route('/newclient', methods=('GET', 'POST'))
def newclient():
    session['clientid'] = None
    session['clientname'] = ''
    return redirect(url_for('.clientinfo'))

@bp.route('/clientinfo', methods=('GET', 'POST'))
def clientinfo():
    clientid = session.get('clientid')
    ci = ClientInfo.query.filter_by(clientid=clientid).one_or_none()
    form = ClientInfoForm(request.form, obj=ci)

    if request.method =='GET':
        return render_template('intake/clientinfo.html', form=form)

    fullname = f'{request.form["firstname"]} {request.form["lastname"]}'
    address = f'{request.form["street"]}, {request.form["city"]}, {request.form["state"]} {request.form["zipcode"]}'

    if not ci:
        ci = ClientInfo(fullname=fullname, address=address)
        form.populate_obj(ci)
        db.session.add(ci)
        db.session.commit()

        session['clientid'] = ci.clientid
        session['clientname'] = fullname
    else:
        form.populate_obj(ci)
        db.session.commit()

    return redirect(url_for('.consent'))

@bp.route('/consent', methods=('GET', 'POST'))
def consent():
    clientid = session.get('clientid')
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    cc = ClientConsent.query.filter_by(clientid=clientid).one_or_none()

    form = ClientConsentForm(obj=cc, fullname=ci.fullname, guardianname=ci.guardianname)

    if request.method == 'GET':
        return render_template('intake/consent.html', form=form)

    if not cc:
        cc = ClientConsent(clientid=clientid)
        form.populate_obj(cc)
        db.session.add(cc)
    else:
        form.populate_obj(cc)
    db.session.commit()

    # TODO: this needs to be saved somewhere
    # html = render_template('intake/consent.html', form=form, pdf=True)
    # pdf = render_pdf(HTML(string=html))
    return redirect(url_for('.release'))

@bp.route('/release', methods=('GET', 'POST'))
def release():
    clientid = session['clientid']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    cr = ClientRelease.query.filter_by(clientid=clientid).one_or_none()

    form = ClientReleaseForm(obj=cr,
                             fullname=ci.fullname,
                             guardianname=ci.guardianname,
                             emergency_contact=ci.emergency_contact,
                             emergency_phone=ci.emergency_phone,
                             dob=ci.dob,
                             address=ci.address,
                             phone=ci.phone,
                             email=ci.email)

    if request.method == 'GET':
        return render_template('intake/release.html', form=form)

    if not cr:
        cr = ClientRelease(clientid=clientid)
        form.populate_obj(cr)
        db.session.add(cr)
    else:
        form.populate_obj(cr)
    db.session.commit()

    # TODO: store pdf
    # html = render_template('intake/release.html', form=form, pdf=True)
    # pdf = render_pdf(HTML(string=html))
    return redirect(url_for('.policies'))

@bp.route('/policies', methods=('GET', 'POST'))
def policies():
    clientid = session['clientid']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    cp = ClientPolicies.query.filter_by(clientid=clientid).one_or_none()

    form = ClientSignForm(obj=cp, fullname=ci.fullname, guardianname=ci.guardianname)

    if request.method == 'GET':
        return render_template('intake/policies.html', form=form)

    if not cp:
        cp = ClientPolicies(clientid=clientid)
        form.populate_obj(cp)
        db.session.add(cp)
    else:
        form.populate_obj(cp)
    db.session.commit()

    # TODO: store pdf
    # html = render_template('intake/policies.html', form=form, pdf=True)
    # pdf = render_pdf(HTML(string=html))
    return redirect(url_for('.send'))

@bp.route('/send', methods=('GET', 'POST'))
def send():
    clientid = session['clientid']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()

    if ci.receive_docs is None:
        form = ClientReceiveForm()
    else:
        form = ClientReceiveForm(receive_docs=ci.receive_docs)

    if request.method == 'GET':
        return render_template('intake/send.html', form=form)

    if 'receive_docs' in request.form and request.form['receive_docs']:
        ci.receive_docs = True
    else:
        ci.receive_docs = False
    db.session.commit()

    return redirect(url_for('main.index'))

@bp.route('/consult', methods=('GET', 'POST'))
def consult():
    clientid = session['clientid']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    cc = ClientConsultContract.query.filter_by(clientid=clientid).one_or_none()

    form = ClientSignForm(obj=cc, fullname=ci.fullname, guardianname=ci.guardianname)

    if request.method == 'GET':
        return render_template('intake/consult.html', form=form)

    if not cc:
        cc = ClientConsultContract(clientid=clientid)
        form.populate_obj(cc)
        db.session.add(cc)
    else:
        form.populate_obj(cc)
    db.session.commit()

    # TODO: store pdf
    # html = render_template('intake/consult.html', form=form, pdf=True)
    # pdf = render_pdf(HTML(string=html))
    return redirect(url_for('main.index'))

@bp.route('/subscription', methods=('GET', 'POST'))
def subscription():
    clientid = session['clientid']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    cs = ClientSubscriptionContract.query.filter_by(clientid=clientid).one_or_none()

    form = ClientSignForm(obj=cs, fullname=ci.fullname, guardianname=ci.guardianname)

    if request.method == 'GET':
        return render_template('intake/subscription.html', form=form)

    if not cs:
        cs = ClientSubscriptionContract(clientid=clientid)
        form.populate_obj(cs)
        db.session.add(cs)
    else:
        form.populate_obj(cs)
    db.session.commit()

    # TODO: store pdf
    # html = render_template('intake/subscription.html', form=form, pdf=True)
    # pdf = render_pdf(HTML(string=html))
    return redirect(url_for('main.index'))

@bp.route('/individual', methods=('GET', 'POST'))
def individual():
    clientid = session['clientid']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    cs = ClientIndividualContract.query.filter_by(clientid=clientid).one_or_none()

    form = ClientIndividualContractForm(obj=cs,
                                        fullname=ci.fullname,
                                        guardianname=ci.guardianname)

    if request.method == 'GET':
        return render_template('intake/individual.html', form=form)

    if not cs:
        cs = ClientIndividualContract(clientid=clientid)
        form.populate_obj(cs)
        db.session.add(cs)
    else:
        form.populate_obj(cs)
    db.session.commit()

    # TODO: store pdf
    # html = render_template('intake/individual.html', form=form, pdf=True)
    # pdf = render_pdf(HTML(string=html))
    return redirect(url_for('main.index'))
