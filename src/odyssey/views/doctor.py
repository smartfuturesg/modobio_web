import datetime

from flask import render_template, Blueprint, session, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import DateField, FormField, StringField, TextAreaField

from odyssey import db
from odyssey.models import ClientInfo, MedicalHistory

bp = Blueprint('doctor', __name__)


class MedicalHistoryDiagnosticForm(FlaskForm):
    title = 'Diagnostic testing'
    xray = StringField('X-ray')
    ctscan = StringField('CT scan')
    endoscopy = StringField('Endoscopy or colonoscopy')
    mri = StringField('MRI')
    ultrasound = StringField('Ultrasound')
    other = StringField('Other diagnostic testing')


class MedicalHistoryGeneralForm(FlaskForm):
    title = 'General'
    headaches = StringField('Headache or migranes')
    blackouts = StringField('Blackouts')
    vertigo = StringField('Dizziness or vertigo')
    sinus = StringField('Sinus problems')
    falling = StringField('History of falling')
    balance = StringField('Balance issues')
    vision = StringField('Vision loss')
    hearing = StringField('Hearing loss')
    memory = StringField('Memory loss')
    insomnia = StringField('Insomnia')
    other = StringField('Other general')


class MedicalHistoryBloodForm(FlaskForm):
    title = 'Cardiovascular and blood'
    bloodpressure = StringField('High blood pressure')
    heartattack = StringField('Heart attack or myocardial infarction')
    heartdissease = StringField('Hear dissease')
    congestive = StringField('Congestive heart failure')
    aneurysm = StringField('Aneurysm')
    bleeding = StringField('Bleeding disorder')
    bloodclots = StringField('Blood clots or deep vein trombosis')
    anemia = StringField('Anemia')
    chestpain = StringField('Chest pain or angina')
    arrythmia = StringField('Arrythmia')
    cholesterol = StringField('High cholesterol')
    other = StringField('Other cardiovascular')


class MedicalHistoryDigestiveForm(FlaskForm):
    title = 'Digestive'
    irritablebowel = StringField('Irritable bowel syndrome')
    crohns = StringField('Crohn\'s disease')
    celiac = StringField('Celiac disease')
    reflux = StringField('Gastro-esophageal reflux or gastritis')
    ulcer = StringField('Ulcer')
    loosestool = StringField('Frequent loose stools')
    constipation = StringField('Frequent constipation')
    eatingdiscomfort = StringField('Discomfort after meals')
    hiatalhernia = StringField('Hiatal hernia')
    swallowing = StringField('Swallowing dysfunction')
    liver = StringField('Liver disorder')
    other = StringField('Other digestive disorder')


class MedicalHistorySkeletalForm(FlaskForm):
    title = 'Musculoskeletal and orthopedic'
    arthritis = StringField('Osteo-arthritis')
    fractures = StringField('Fractures')
    compressionfracture = StringField('Compression fracture')
    stressfracture = StringField('Stress fracture')
    dislocation = StringField('Dislocation')
    inguinalhernia = StringField('Inguinal hernia')
    otherhernia = StringField('Other hernia')
    diastatis = StringField('Diastasis recti')
    carpaltunnel = StringField('Carpal tunnel')
    thoracicoutlet = StringField('Thoracic outlet syndrome')
    spinalstenosis = StringField('Spinal stenosis')
    sciatica = StringField('Sciatica')
    spondylolisthesis = StringField('Spondylolisthesis')
    dischernia = StringField('Herniated disc')
    temporomandibular = StringField('Temporomandibular disorder')
    other = StringField('Other ortho injuries')


class MedicalHistoryImmuneForm(FlaskForm):
    title = 'Immune, endocrine, and metabolic'
    diabetes = StringField('Diabetes')
    lowbloodsugar = StringField('Low blood sugar')
    hepatitis = StringField('Hepatitis')
    hiv = StringField('HIV/AIDS')
    tuberculosis = StringField('Tuberculosis')
    cancer = StringField('Cancer')
    thyroid = StringField('Thyroid dysfunction')
    autoimmune = StringField('Autoimmune disease')
    osteoporosis = StringField('Osteoporosis or osteopenia')
    gout = StringField('Gout')
    rheuma = StringField('Rheumatoid arthritis')
    lupus = StringField('Lupus')
    fibromyalgia = StringField('Fibromyalgia')
    other = StringField('Other inflammatory condition')


class MedicalHistorySurgeryForm(FlaskForm):
    title = 'Surgical history'
    bypass = StringField('Bypass or CABG surgery')
    pacemaker = StringField('Pacemaker or defibrilator')
    stents = StringField('Vascular surgery or stents')
    abdominal = StringField('Abdominal surgery')
    gastric = StringField('Gastric bypass surgery')
    hysterectomy = StringField('Hysterectomy')
    tuballigation = StringField('Tubal ligation')
    laparoscopy = StringField('Laparoscopy')
    bladder = StringField('Bladder surgery')
    csection = StringField('C-section')
    hernia = StringField('Hernia surgery')
    galbladder = StringField('Gal bladder surgery')
    orthopedic = StringField('Orthopedic surgery')
    back = StringField('Back or neck surgery')
    plastic = StringField('Plastic surgery')
    other = StringField('Other surgery')


class MedicalHistoryUroForm(FlaskForm):
    title = 'Urogenital and gynecological'
    urological = StringField('Urological disorder')
    kidney = StringField('Kidney disease')
    incontinence = StringField('Incontinence')
    endometriosis = StringField('Endometriosis')
    gynecology = StringField('Gynecological disorder')
    fibroids = StringField('Fibroids or cysts')
    childbirth = StringField('Child birth')
    other = StringField('Other urogenital disorder')


class MedicalHistoryRespiratoryForm(FlaskForm):
    title = 'Respiratory'
    smoke = StringField('Do you smoke?')
    asthma = StringField('Asthma')
    emphysema = StringField('Emphysema or COPD')
    pneumonia = StringField('Pneumonia')
    allergies = StringField('Allergies')
    sleepapnea = StringField('Sleep apnea')
    deviatedseptum = StringField('Deviated septum')
    shortbreath = StringField('Shortness of breath')
    other = StringField('Other lung disorders')


class MedicalHistoryNeuroForm(FlaskForm):
    title = 'Nervous system'
    brain = StringField('Head or brain injury')
    stroke = StringField('Stroke or TIA')
    ms = StringField('Multiple Sclerosis')
    neuropathy = StringField('Peripheral neuropathy')
    epilepsy = StringField('Epilepsy or seizures')
    parkinson = StringField('Parkinson\'s disease')
    neuromuscular = StringField('Neuromuscular disorder')
    other = StringField('Other neurological disorder')


class MedicalHistoryTraumaForm(FlaskForm):
    title = 'Trauma'
    whiplash = StringField('Whiplash')
    accident = StringField('Motor vehicle accident')
    concussion = StringField('Concussion')
    other = StringField('Other trauma')


class MedicalHistoryNutritionForm(FlaskForm):
    title = 'Nutritional'
    deficiency = StringField('Nutritional deficiency')
    allergies = StringField('Food allergies')
    eating = StringField('Eating disorder')
    other = StringField('Other nutritional')


class MedicalHistoryForm(FlaskForm):
    dob = DateField('Date of birth')

    healthcare_contact = StringField('Primary healthcare provider name')
    healthcare_phone = StringField('Primary healthcare provider phone')

    last_examination_date = DateField('Last doctor\'s visit')
    last_examination_reason = StringField('Reason for last visit')

    goals = TextAreaField('Goals')
    concerns = TextAreaField('Health concerns or conditions')
    family_history = TextAreaField('Family history')
    allergies = TextAreaField('Allergies and reactions')
    medication = TextAreaField('Current medication and supplements (include dosage)')

    diagnostic = FormField(MedicalHistoryDiagnosticForm, separator='_')
    general = FormField(MedicalHistoryGeneralForm, separator='_')
    blood = FormField(MedicalHistoryBloodForm, separator='_')
    digestive = FormField(MedicalHistoryDigestiveForm, separator='_')
    skeletal = FormField(MedicalHistorySkeletalForm, separator='_')
    immune = FormField(MedicalHistoryImmuneForm, separator='_')
    surgery = FormField(MedicalHistorySurgeryForm, separator='_')
    uro = FormField(MedicalHistoryUroForm, separator='_')
    respiratory = FormField(MedicalHistoryRespiratoryForm, separator='_')
    neuro = FormField(MedicalHistoryNeuroForm, separator='_')
    trauma = FormField(MedicalHistoryTraumaForm, separator='_')
    nutrition = FormField(MedicalHistoryNutritionForm, separator='_')


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

    if md:
        form.populate_obj(md)
    else:
        form = dict(request.form)
        form['clientid'] = clientid
        form.pop('dob')
        form.pop('healthcare_contact')
        form.pop('healthcare_phone')
        md = MedicalHistory(**form)
        db.session.add(md)

    db.session.commit()

    return redirect(url_for('main.index'))
