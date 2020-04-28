import datetime

from flask import render_template, Blueprint, session, redirect, request, url_for

from odyssey import db
from odyssey.forms.doctor import MedicalHistoryForm
from odyssey.models.doctor import MedicalHistory
from odyssey.models.intake import ClientInfo

bp = Blueprint('doctor', __name__)

@bp.route('/history', methods=('GET', 'POST'))
def history():
    clientid = session['clientid']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    md = MedicalHistory.query.filter_by(clientid=clientid).one_or_none()

    # Map column_names to nested subform.name
    table2form = {
        'diagnostic': {},
        'general': {},
        'blood': {},
        'digestive': {},
        'skeletal': {},
        'immune': {},
        'surgery': {},
        'uro': {},
        'respiratory': {},
        'neuro': {},
        'trauma': {},
        'nutrition': {}
    }

    if md:
        for col in md.__table__.c:
            parts = col.name.split('_')
            if len(parts) > 1 and parts[0] in table2form:
                table2form[parts[0]][parts[1]] = getattr(md, col.name, '')

    form = MedicalHistoryForm(
        obj=md,
        dob=ci.dob,
        healthcare_contact=ci.healthcare_contact,
        healthcare_phone=ci.healthcare_phone,
        **table2form
    )

    if request.method == 'GET':
        return render_template('doctor/history.html', form=form)

    form = dict(request.form)

    if md:
        md.update(form)
    else:
        md = MedicalHistory(clientid=clientid)
        md.update(form)
        db.session.add(md)

    db.session.commit()

    return redirect(url_for('main.index'))
