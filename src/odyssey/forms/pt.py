from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import BooleanField, FormField, HiddenField, IntegerField, StringField, TextAreaField


class PTHistoryForm(FlaskForm):
    exercise = TextAreaField('Please describe your current exercise routine, how often, and where/with whom. Leave empty if you do not exercise.')

    has_pt = BooleanField('Physical therapy')
    has_chiro = BooleanField('Chiropractor')
    has_massage = BooleanField('Massage therapy')
    has_surgery = BooleanField('Surgery')
    has_medication = BooleanField('Medication')
    has_acupuncture = BooleanField('Acupuncture')

    pain_areas = HiddenField()

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
    timestamp = StringField('Assessment date', default=datetime.now())
    isa_left = IntegerField('ISA left')
    isa_right = IntegerField('ISA right')
    isa_dynamic = BooleanField('Dynamic?')

    left_shoulder = FormField(MobilityAssessmentLSForm, separator='_')
    right_shoulder = FormField(MobilityAssessmentRSForm, separator='_')
    left_hip = FormField(MobilityAssessmentLHForm, separator='_')
    right_hip = FormField(MobilityAssessmentRHForm, separator='_')
