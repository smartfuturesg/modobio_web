import datetime

from flask import flash, render_template, Blueprint, session, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateTimeField, FormField, IntegerField, SelectMultipleField, StringField, TextAreaField

from odyssey import db
from odyssey.constants import THERAPIES, YESNO, BOOLIFY
from odyssey.models import MobilityAssessment, PTHistory

bp = Blueprint('pt', __name__)


class PTHistoryForm(FlaskForm):
    exercise = TextAreaField('Please describe your current exercise routine, how often, and where/with whom. Leave empty if you do not exercise.')

    treatment = SelectMultipleField('Did you receive any of the following treatments? Select all that apply.',
        choices=THERAPIES, render_kw={'size': len(THERAPIES)})
    
    pain_areas = StringField('Mark areas of pain with an "X"', default='This will be implemented as a clickable silhouette of a human.')

    best_pain = IntegerField('Best pain')
    worst_pain = IntegerField('Worst pain')
    current_pain = IntegerField('Current pain')

    makes_worse = StringField('What makes your symptoms worse, including time of day?')
    makes_better = StringField('What makes your symptoms better, including time of day?')


class MobilityAssessmentQuadrantForm(FlaskForm):
    er = IntegerField('ER')
    ir = IntegerField('IR')
    abd = IntegerField('ABD')
    add = IntegerField('ADD')
    flexion = IntegerField('Flexion')
    extension = IntegerField('Extension')


class MobilityAssessmentLSForm(MobilityAssessmentQuadrantForm):
    title = 'Left shoulder'


class MobilityAssessmentRSForm(MobilityAssessmentQuadrantForm):
    title = 'Right shoulder'


class MobilityAssessmentLHForm(MobilityAssessmentQuadrantForm):
    title = 'Left hip'


class MobilityAssessmentRHForm(MobilityAssessmentQuadrantForm):
    title = 'Right hip'


class MobilityAssessmentForm(FlaskForm):
    timestamp = StringField('Assessment date', default=datetime.datetime.now())
    isa_left = IntegerField('ISA left')
    isa_right = IntegerField('ISA right')
    isa_dynamic = BooleanField('Dynamic?')

    left_shoulder = FormField(MobilityAssessmentLSForm, separator='_')
    right_shoulder = FormField(MobilityAssessmentRSForm, separator='_')
    left_hip = FormField(MobilityAssessmentLHForm, separator='_')
    right_hip = FormField(MobilityAssessmentRHForm, separator='_')


@bp.route('/history', methods=('GET', 'POST'))
def history():
    clientid = session['clientid']
    pt = PTHistory.query.filter_by(clientid=clientid).one_or_none()

    form = PTHistoryForm(obj=pt)

    if request.method == 'GET':
        return render_template('pt/history.html', form=form)

    if pt:
        form.populate_obj(pt)
    else:
        pt = PTHistory(**request.form, clientid=clientid)
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
    if form['isa_dynamic'] == 'y':
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
