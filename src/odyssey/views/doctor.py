import datetime

from flask import render_template, Blueprint, session, redirect, request, url_for

from odyssey import db
from odyssey.forms.doctor import MedicalHistoryForm, MedicalPhysicalExamForm
from odyssey.models.doctor import MedicalHistory, MedicalPhysicalExam
from odyssey.models.intake import ClientInfo

bp = Blueprint('doctor', __name__)

@bp.route('/history', methods=('GET', 'POST'))
def history():
    clientid = session['clientid']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    md = MedicalHistory.query.filter_by(clientid=clientid).one_or_none()

    # Map column_names to nested subform.name
    # table2form = {
    #     'diagnostic': {},
    #     'general': {},
    #     'blood': {},
    #     'digestive': {},
    #     'skeletal': {},
    #     'immune': {},
    #     'surgery': {},
    #     'uro': {},
    #     'respiratory': {},
    #     'neuro': {},
    #     'trauma': {},
    #     'nutrition': {}
    # }
    #
    # if md:
    #     for col in md.__table__.c:
    #         parts = col.name.split('_')
    #         if len(parts) > 1 and parts[0] in table2form:
    #             table2form[parts[0]][parts[1]] = getattr(md, col.name, '')

    form = MedicalHistoryForm(
        obj=md,
        dob=ci.dob,
        healthcare_contact=ci.healthcare_contact,
        healthcare_phone=ci.healthcare_phone
    )

    if request.method == 'GET':
        return render_template('doctor/history.html', form=form)

    form = dict(request.form)

    # Error if date = ""
    # TODO: this should be fixed with better input validation
    if not form['last_examination_date']:
        form['last_examination_date'] = None

    if md:
        md.update(form)
    else:
        md = MedicalHistory(clientid=clientid)
        md.update(form)
        db.session.add(md)

    db.session.commit()

    return redirect(url_for('.physical'))

@bp.route('/physical', methods=('GET', 'POST'))
def physical():
    clientid = session['clientid']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    md = MedicalPhysicalExam.query.filter_by(clientid=clientid).one_or_none()

    form = MedicalPhysicalExamForm(obj=md)

    if request.method == 'GET':
        return render_template('doctor/physical.html', form=form)

    if md:
        form.populate_obj(md)
    else:
        md = MedicalPhysicalExam(clientid=clientid)
        form.populate_obj(md)
        db.session.add(md)

    db.session.commit()

    return redirect(url_for('main.index'))
