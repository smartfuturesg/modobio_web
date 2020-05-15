from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, FloatField, \
                    IntegerField, StringField, TextAreaField


class MedicalHistoryForm(FlaskForm):
    dob = DateField('Date of birth')

    healthcare_contact = StringField('Primary healthcare provider name')
    healthcare_phone = StringField('Primary healthcare provider phone')

    last_examination_date = DateField('Last doctor\'s visit')
    last_examination_reason = StringField('Reason for last visit')

    goals = TextAreaField('Goals')
    concerns = TextAreaField('Health concerns or conditions')
    family_history = TextAreaField('Family history')
    social_history = TextAreaField('Social history including smoking, drinking, and drug use')
    allergies = TextAreaField('Allergies and reactions')
    medication = TextAreaField('Current medication and supplements (include dosage)')

    diagnostic_xray = StringField('X-ray')
    diagnostic_ctscan = StringField('CT scan')
    diagnostic_endoscopy = StringField('Endoscopy or colonoscopy')
    diagnostic_mri = StringField('MRI')
    diagnostic_ultrasound = StringField('Ultrasound')
    diagnostic_other = StringField('Other diagnostic testing')


class MedicalPhysicalExamForm(FlaskForm):
    vital_heartrate = IntegerField('Heart rate')
    vital_respiratoryrate = IntegerField('Respiratory rate')
    vital_systolic = IntegerField('Systolic blood pressure')
    vital_diastolic = IntegerField('Diastolic blood pressure')
    vital_temperature = FloatField('Temperature')

    cardiac_rrr = BooleanField('RRR')
    cardiac_s1s2 = BooleanField('S1S2')
    cardiac_murmurs = BooleanField('Murmurs')
    cardiac_murmurs_info = StringField()
    cardiac_rubs = BooleanField('Rubs')
    cardiac_gallops = BooleanField('Gallops')

    pulmonary_clear = BooleanField('Clear to auscultation bilaterally')
    pulmonary_wheezing = BooleanField('Wheezing')
    pulmonary_wheezing_info = StringField()
    pulmonary_rales = BooleanField('Rales')
    pulmonary_rhonchi = BooleanField('Rhonchi')

    abdominal_soft = BooleanField('Soft')
    abdominal_hard = BooleanField('Non tender')
    abdominal_bowel = BooleanField('Positive bowel sounds')
    abdominal_hsm = BooleanField('Hepatosplenomegaly')
    abdominal_hsm_info = StringField()

    notes = TextAreaField('Other notes')