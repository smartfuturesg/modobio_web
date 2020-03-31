import datetime

from flask import render_template, Blueprint, session, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, FormField, HiddenField, IntegerField, StringField, TextAreaField

from odyssey import db
from odyssey.models import ClientInfo

bp = Blueprint('doctor', __name__)


class MedicalHistoryCheckForm(FlaskForm):
    # This is a long list of tick boxes with labels.
    # They are grouped with a label (HiddenField, only
    # render the label). This form is included in
    # MedicalHistoryForm, so it can be in a loop.
    label_general = HiddenField('General')
    has_headaches = BooleanField('Headache or migranes')
    has_blackouts = BooleanField('Blackouts')
    has_vertigo = BooleanField('Dizziness or vertigo')
    has_sinus = BooleanField('Sinus problems')
    has_fallen = BooleanField('History of falling')
    has_balance = BooleanField('Balance issues')
    has_vision = BooleanField('Vision loss')
    has_hearing = BooleanField('Hearing loss')
    has_memory = BooleanField('Memory loss')
    has_insomnia = BooleanField('Insomnia')

    label_blood = HiddenField('Cardiovascular and blood')
    has_bloodpressure = BooleanField('High blood pressure')
    has_heartattack = BooleanField('Heart attack or myocardial infarction')
    has_heartdissease = BooleanField('Hear dissease')
    has_congesitive = BooleanField('Congestive heart failure')
    has_aneurysm = BooleanField('Aneurysm')
    has_bleeding = BooleanField('Bleeding disorder')
    has_bloodclots = BooleanField('Blood clots or deep vein trombosis')
    has_anemia = BooleanField('Anemia')
    has_chestpain = BooleanField('Chest pain or angina')
    has_arrythmia = BooleanField('Arrythmia')
    has_cholesterol = BooleanField('High cholesterol')

    label_digestive = HiddenField('Digestive')
    has_irritablebowel = BooleanField('Irritable bowel syndrome')
    has_crohns = BooleanField('Crohn\'s disease')
    has_celiac = BooleanField('Celiac disease')
    has_reflux = BooleanField('Gastro-esophageal reflux or gastritis')
    has_ulcer = BooleanField('Ulcer')
    has_loosestool = BooleanField('Frequent loose stools')
    has_constipation = BooleanField('Frequent constipation')
    has_eatingdiscomfort = BooleanField('Discomfort after meals')
    has_hiatalhernia = BooleanField('Hiatal hernia')
    has_swallowing = BooleanField('Swallowing dysfunction')
    has_liver = BooleanField('Liver disorder')

    label_ortho = HiddenField('Musculoskeletal and orthopedic')
    has_arthritis = BooleanField('Osteo-arthritis')
    has_fractures = BooleanField('Fractures')
    has_compressionfracture = BooleanField('Compression fracture')
    has_stressfracture = BooleanField('Stress fracture')
    has_dislocation = BooleanField('Dislocation')
    has_inguinalhernia = BooleanField('Inguinal hernia')
    has_otherhernia = BooleanField('Other hernia')
    has_diastatis = BooleanField('Diastasis recti')
    has_carpaltunnel = BooleanField('Carpal tunnel')
    has_thoracicoutlet = BooleanField('Thoracic outlet syndrome')
    has_spinalstenosis = BooleanField('Spinal stenosis')
    has_sciatica = BooleanField('Sciatica')
    has_spondylolisthesis = BooleanField('Spondylolisthesis')
    has_dischernia = BooleanField('Herniated disc')
    has_temporomandibular = BooleanField('Temporomandibular disorder')
    has_otherortho = BooleanField('Other ortho injuries')
    ortho = StringField('', render_kw={'placeholder': 'Please describe ortho injuries.'})

    label_immune = HiddenField('Immune, endocrine, and metabolic')
    has_diabetes1 = BooleanField('Diabetes type 1')
    has_diabetes2 = BooleanField('Diabetes type 2')
    has_lowbloodsugar = BooleanField('Low blood sugar')
    has_hepatitisA = BooleanField('Hepatitis A')
    has_hepatitisB = BooleanField('Hepatitis B')
    has_hepatitisC = BooleanField('Hepatitis C')
    has_hiv = BooleanField('HIV/AIDS')
    has_tuberculosis = BooleanField('Tuberculosis')
    has_cancer = BooleanField('Cancer')
    cancer = StringField('', render_kw={'placeholder': 'Please describe type and status of cancer.'})
    has_thyroid = BooleanField('Thyroid dysfunction')
    has_autoimmune = BooleanField('Autoimmune disease')
    autoimmune = StringField('', render_kw={'placeholder': 'Please describe autoimmune disease.'})
    has_osteoporosis = BooleanField('Osteoporosis or osteopenia')
    has_gout = BooleanField('Gout')
    has_rheuma = BooleanField('Rheumatoid arthritis')
    has_lupus = BooleanField('Lupus')
    has_fibromyalgia = BooleanField('Fibromyalgia')
    has_otherinflammatory = BooleanField('Other inflammatory condition')
    inflammatory = StringField('', render_kw={'placeholder': 'Please describe type of inflammatory condition.'})

    label_surgical = HiddenField('Surgical history')
    has_bypass = BooleanField('Bypass or CABG surgery')
    has_pacemaker = BooleanField('Pacemaker or defibrilator')
    has_stents = BooleanField('Vascular surgery or stents')
    has_abdominal = BooleanField('Abdominal surgery')
    has_gastric = BooleanField('Gastric bypass surgery')
    has_hysterectomy = BooleanField('Hysterectomy')
    has_tuballigation = BooleanField('Tubal ligation')
    has_laparoscopy = BooleanField('Laparoscopy')
    has_bladder = BooleanField('Bladder surgery')
    has_csection = BooleanField('C-section')
    has_herniasurgery = BooleanField('Hernia surgery')
    has_galbladder = BooleanField('Gal bladder surgery')
    has_orthopedic = BooleanField('Orthopedic surgery')
    has_back = BooleanField('Back or neck surgery')
    has_plastic = BooleanField('Plastic surgery')
    has_othersurgery = BooleanField('Other surgery')
    surgery = StringField('', render_kw={'placeholder': 'Please describe surgeries.'})

    label_urogenital = HiddenField('Urogenital and gynecological')
    has_urological = BooleanField('Urological disorder')
    has_kidney = BooleanField('Kidney disease')
    has_incontinence = BooleanField('Incontinence')
    has_endometriosis = BooleanField('Endometriosis')
    has_gynecology = BooleanField('Gynecological disorder')
    has_fibroids = BooleanField('Fibroids or cysts')
    has_childbirth = BooleanField('Child birth')
    childbirths = IntegerField('', render_kw={'placeholder': 'Please give number of child births.'})

    label_respiatory = HiddenField('Respiratory')
    has_smoke = BooleanField('Do you smoke?')
    smoke = StringField('', render_kw={'placeholder': 'Please describe how often.'})
    has_asthma = BooleanField('Asthma')
    has_emphysema = BooleanField('Emphysema or COPD')
    has_pneumonia = BooleanField('Pneumonia')
    has_allergies = BooleanField('Allergies')
    has_sleepapnea = BooleanField('Sleep apnea')
    has_deviatedseptum = BooleanField('Deviated septum')
    has_shortbreath = BooleanField('Shortness of breath')
    has_otherlung = BooleanField('Other lung disorders')
    lung = StringField('', render_kw={'placeholder': 'Please describe lung disorder.'})

    label_nervous = HiddenField('Nervous system')
    has_brain = BooleanField('Head or brain injury')
    has_stroke = BooleanField('Stroke or TIA')
    has_ms = BooleanField('Multiple Sclerosis')
    has_neuropathy = BooleanField('Peripheral neuropathy')
    has_epilepsy = BooleanField('Epilepsy or seizures')
    has_parkinson = BooleanField('Parkinson\'s disease')
    has_neuromuscular = BooleanField('Neuromuscular disorder')
    has_otherneuro = BooleanField('Other neurological disorder')
    neuro = StringField('', render_kw={'placeholder': 'Please describe neurological disorder.'})

    label_trauma = HiddenField('Trauma')
    has_whiplash = BooleanField('Whiplash')
    has_accident = BooleanField('Motor vehicle accident')
    has_concussion = BooleanField('Concussion')
    has_othertrauma = BooleanField('Other trauma')
    trauma = StringField('', render_kw={'placeholder': 'Please describe trauma.'})

    label_nutritional = HiddenField('Nutritional')
    has_nutritional = BooleanField('Nutritional deficiency')
    has_foodallergiues = BooleanField('Food allergies')
    has_eating = BooleanField('Eating disorder')    
    

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
    dob = DateField('Date of birth', render_kw={'type': 'date'})

    healthcare_contact = StringField('Primary healthcare provider name')
    healthcare_phone = StringField('Primary healthcare provider phone')

    last_examination_date = DateField('Last doctor\'s visit', render_kw={'type': 'date'})
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
    fullname = session['client_name']
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