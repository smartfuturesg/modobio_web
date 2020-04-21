import datetime

from flask import render_template, Blueprint, session, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, FormField, HiddenField, IntegerField, StringField, TextAreaField

from odyssey import db
from odyssey.models import ClientInfo

bp = Blueprint('doctor', __name__)


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


class MedicalHistoryBloodForm(FlaskForm):
    title = 'Cardiovascular and blood'
    bloodpressure = StringField('High blood pressure')
    heartattack = StringField('Heart attack or myocardial infarction')
    heartdissease = StringField('Hear dissease')
    congesitive = StringField('Congestive heart failure')
    aneurysm = StringField('Aneurysm')
    bleeding = StringField('Bleeding disorder')
    bloodclots = StringField('Blood clots or deep vein trombosis')
    anemia = StringField('Anemia')
    chestpain = StringField('Chest pain or angina')
    arrythmia = StringField('Arrythmia')
    cholesterol = StringField('High cholesterol')


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
    otherortho = StringField('Other ortho injuries')


class MedicalHistoryImmuneForm(FlaskForm):
    title = 'Immune, endocrine, and metabolic'
    diabetes1 = StringField('Diabetes type 1')
    diabetes2 = StringField('Diabetes type 2')
    lowbloodsugar = StringField('Low blood sugar')
    hepatitisA = StringField('Hepatitis A')
    hepatitisB = StringField('Hepatitis B')
    hepatitisC = StringField('Hepatitis C')
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
    otherinflammatory = StringField('Other inflammatory condition')


class MedicalHistorySurgicalForm(FlaskForm):
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
    herniasurgery = StringField('Hernia surgery')
    galbladder = StringField('Gal bladder surgery')
    orthopedic = StringField('Orthopedic surgery')
    back = StringField('Back or neck surgery')
    plastic = StringField('Plastic surgery')
    othersurgery = StringField('Other surgery')


class MedicalHistoryUroForm(FlaskForm):
    title = 'Urogenital and gynecological'
    urological = StringField('Urological disorder')
    kidney = StringField('Kidney disease')
    incontinence = StringField('Incontinence')
    endometriosis = StringField('Endometriosis')
    gynecology = StringField('Gynecological disorder')
    fibroids = StringField('Fibroids or cysts')
    childbirth = StringField('Child birth')


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
    otherlung = StringField('Other lung disorders')


class MedicalHistoryNervousForm(FlaskForm):
    title = 'Nervous system'
    brain = StringField('Head or brain injury')
    stroke = StringField('Stroke or TIA')
    ms = StringField('Multiple Sclerosis')
    neuropathy = StringField('Peripheral neuropathy')
    epilepsy = StringField('Epilepsy or seizures')
    parkinson = StringField('Parkinson\'s disease')
    neuromuscular = StringField('Neuromuscular disorder')
    otherneuro = StringField('Other neurological disorder')


class MedicalHistoryTraumaForm(FlaskForm):
    title = 'Trauma'
    whiplash = StringField('Whiplash')
    accident = StringField('Motor vehicle accident')
    concussion = StringField('Concussion')
    othertrauma = StringField('Other trauma')


class MedicalHistoryNutritionForm(FlaskForm):
    title = 'Nutritional'
    nutritional = StringField('Nutritional deficiency')
    foodallergiues = StringField('Food allergies')
    eating = StringField('Eating disorder')    


class MedicalHistoryCheckForm(FlaskForm):
    general = FormField(MedicalHistoryGeneralForm)
    blood = FormField(MedicalHistoryBloodForm)
    digestive = FormField(MedicalHistoryDigestiveForm)
    skeletal = FormField(MedicalHistorySkeletalForm)
    immune = FormField(MedicalHistoryImmuneForm)
    surgical = FormField(MedicalHistorySurgicalForm)
    uro = FormField(MedicalHistoryUroForm)
    respiratory = FormField(MedicalHistoryRespiratoryForm)
    nervous = FormField(MedicalHistoryNervousForm)
    trauma = FormField(MedicalHistoryTraumaForm)
    nutrition = FormField(MedicalHistoryNutritionForm)


class MedicalHistoryDiagnosticForm(FlaskForm):
    has_xray = BooleanField('X-ray')
    xray = StringField('')
    has_ctscan = BooleanField('CT scan')
    ctscan = StringField('')
    has_endoscopy = BooleanField('Endoscopy or colonoscopy')
    endoscopy = StringField('')
    has_mri = BooleanField('MRI')
    mri = StringField('')
    has_ultrasound = BooleanField('Ultrasound')
    ultrasound = StringField('')
    has_otherdiagnostic = BooleanField('Other diagnostic testing')
    otherdiagnostic = StringField('')


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

    diagnostic = FormField(MedicalHistoryDiagnosticForm)
    history = FormField(MedicalHistoryCheckForm)


@bp.route('/history', methods=('GET', 'POST'))
def history():
    clientid = session['clientid']
    fullname = session['clientname']
    ci = ClientInfo.query.filter_by(clientid=clientid).one()
    
    form = MedicalHistoryForm(
        fullname=fullname,
        dob=ci.dob,
        healthcare_contact=ci.healthcare_contact,
        healthcare_phone=ci.healthcare_phone
    )

    if request.method == 'GET':
        return render_template('doctor/history.html', form=form)
    return redirect(url_for('main.index'))