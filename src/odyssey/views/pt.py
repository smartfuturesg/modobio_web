import datetime

from flask import flash, render_template, Blueprint, session, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, FormField, IntegerField, RadioField, SelectMultipleField, StringField, TextAreaField

from odyssey import db
from odyssey.constants import THERAPIES
from odyssey.models import ClientInfo

bp = Blueprint('pt', __name__)


class PTHistoryForm(FlaskForm):
    has_exercise = RadioField('Do you currently exercise?',
        choices=((1, 'Yes'), (0, 'No')),
    )
    
    exercise = TextAreaField('Please describe your exercises, how often, and where/with whom.')

    treatment = SelectMultipleField('Did you receive any of the following treatments? Select all that apply.',
        choices=THERAPIES, render_kw={'size': len(THERAPIES)})
    
    pain_areas = StringField('Mark areas of pain with an "X"', default='How do you want me to implement this? Clickable image of person?')

    best_pain = IntegerField('Best pain')
    worst_pain = IntegerField('Worst pain')
    current_pain = IntegerField('Current pain')

    makes_worse = StringField('What makes your symptoms worse, including time of day?')
    makes_better = StringField('What makes your symptoms better, including time of day?')


class MobilityAssessmentQuadrantForm(FlaskForm):
    er_left_shoulder = IntegerField('ER')
    ir_left_shoulder = IntegerField('IR')
    abd_left_shoulder = IntegerField('ABD')
    add_left_shoulder = IntegerField('ABD')
    flexing_left_shoulder = IntegerField('Flexing')
    extension_left_shoulder = IntegerField('Extension')


class MobilityAssessmentForm(FlaskForm):
    assessment_date = DateField('Assessment date',
        default=datetime.date.today(),
        render_kw={'type': 'date'}
    )
    isa_left = IntegerField('ISA left')
    isa_right = IntegerField('ISA right')
    isa_dynamic = BooleanField('Dynamic?')

    left_shoulder = FormField(MobilityAssessmentQuadrantForm)
    right_shoulder = FormField(MobilityAssessmentQuadrantForm)
    left_hip = FormField(MobilityAssessmentQuadrantForm)
    right_hip = FormField(MobilityAssessmentQuadrantForm)


@bp.route('/history', methods=('GET', 'POST'))
def history():
    if request.method == 'GET':
        return render_template('pt/history.html', form=PTHistoryForm())
    return redirect(url_for('.mobility'))

@bp.route('/mobility', methods=('GET', 'POST'))
def mobility():
    if request.method == 'GET':
        flash('This needs some type of load/save functionality to recall previous assessments and scroll through them.')
        return render_template('pt/mobility.html', form=MobilityAssessmentForm())
    return redirect(url_for('main.index'))
