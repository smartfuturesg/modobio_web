from flask import flash, render_template, Blueprint, session, redirect, request, url_for

from odyssey import db
from odyssey.forms.pt import MobilityAssessmentForm, PTHistoryForm
from odyssey.models.pt import MobilityAssessment, PTHistory

bp = Blueprint('pt', __name__)


@bp.route('/history', methods=('GET', 'POST'))
def history():
    clientid = session['clientid']
    pt = PTHistory.query.filter_by(clientid=clientid).one_or_none()

    form = PTHistoryForm(obj=pt)

    if request.method == 'GET':
        return render_template('pt/history.html', form=form)

    form = dict(request.form)
    for k in ('has_pt', 'has_chiro', 'has_massage', 'has_surgery',
              'has_medication', 'has_acupuncture'):
        if k in form and form[k]:
            form[k] = True
        else:
            form[k] = False

    if pt:
        pt.update(form)
    else:
        pt = PTHistory(**form, clientid=clientid)
        db.session.add(pt)

    db.session.commit()

    return redirect(url_for('.mobility'))

@bp.route('/mobility', methods=('GET', 'POST'))
def mobility():
    clientid = session['clientid']
    mb = MobilityAssessment.query.filter_by(clientid=clientid).one_or_none()

    # Map column_names to nested subform.name
    table2form = {
        'left_shoulder': {},
        'right_shoulder': {},
        'left_hip': {},
        'right_hip': {}
    }

    if mb:
        for col in mb.__table__.c:
            parts = col.name.split('_')
            if len(parts) == 3:
                subform = parts[0] + '_' + parts[1]
                element = parts[2]
                table2form[subform][element] = getattr(mb, col.name, '')

    form = MobilityAssessmentForm(obj=mb, **table2form)

    if request.method == 'GET':
        flash('This needs some type of load/save functionality to recall previous assessments and scroll through them.')
        return render_template('pt/mobility.html', form=form)

    form = dict(request.form)

    isa = False
    if 'isa_dynamic' in form and form['isa_dynamic']:
        form['isa_dynamic'] = True
    else:
        form['isa_dynamic'] = False

    if mb:
        mb.update(form)
    else:
        mb = MobilityAssessment(**form, clientid=clientid)
        db.session.add(mb)

    db.session.commit()

    return redirect(url_for('main.index'))
