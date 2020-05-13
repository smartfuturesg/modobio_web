"""
Database tables for the doctor's portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'Medical'.
"""

from odyssey import db

class MedicalHistory(db.Model):
    """ Medical history table

    This table stores the medical history of a client. The information is taken
    only once, during the initial consult.
    """
    __tablename__ = 'MedicalHistory'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Index

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    last_examination_date = db.Column(db.Date)
    """
    Last time client visited a doctor.

    :type: :class:`datetime.date`
    """

    last_examination_reason = db.Column(db.String(1024))
    """
    Explanation of reason for last visit to a doctor.

    :type: str, max length 1024
    """

    goals = db.Column(db.Text)
    """
    Client's goals for visiting Modo Bio.

    :type: str
    """

    concerns = db.Column(db.Text)
    """
    Client's concerns while visiting Modo Bio.

    :type: str
    """

    family_history = db.Column(db.Text)
    """
    Client's medical family history.

    :type: str
    """

    social_history = db.Column(db.Text)
    """
    Client's health related social history.

    :type: str
    """

    allergies = db.Column(db.Text)
    """
    Client's allergies.

    :type: str
    """

    medication = db.Column(db.Text)
    """
    Client's medication.

    :type: str
    """

    diagnostic_xray = db.Column(db.String(1024))
    """
    Client recently had an X-ray, with reason and outcome.

    :type: str, max length 1024
    """

    diagnostic_ctscan = db.Column(db.String(1024))
    """
    Client recently had a CT scan, with reason and outcome.

    :type: str, max length 1024
    """

    diagnostic_endoscopy = db.Column(db.String(1024))
    """
    Client recently had an endoscopy, with reason and outcome.

    :type: str, max length 1024
    """

    diagnostic_mri = db.Column(db.String(1024))
    """
    Client recently had a MRI, with reason and outcome.

    :type: str, max length 1024
    """

    diagnostic_ultrasound = db.Column(db.String(1024))
    """
    Client recently had an ultrasound, with reason and outcome.

    :type: str, max length 1024
    """

    diagnostic_other = db.Column(db.String(1024))
    """
    Client recently had an other diagnostic procedure, with reason and outcome.

    :type: str, max length 1024
    """

    general_headaches = db.Column(db.String(1024))
    """
    Client has headaches or migranes.

    :type: str, max length 1024
    """

    general_blackouts = db.Column(db.String(1024))
    """
    Client has blackouts.

    :type: str, max length 1024
    """

    general_vertigo = db.Column(db.String(1024))
    """
    Client has dizziness or vertigo.

    :type: str, max length 1024
    """

    general_sinus = db.Column(db.String(1024))
    """
    Client has sinus problems.

    :type: str, max length 1024
    """

    general_falling = db.Column(db.String(1024))
    """
    Client has a history of falling.

    :type: str, max length 1024
    """

    general_balance = db.Column(db.String(1024))
    """
    Client has balance issues.

    :type: str, max length 1024
    """

    general_vision = db.Column(db.String(1024))
    """
    Client has vision loss.

    :type: str, max length 1024
    """

    general_hearing = db.Column(db.String(1024))
    """
    Client has hearing loss.

    :type: str, max length 1024
    """

    general_memory = db.Column(db.String(1024))
    """
    Client has memory loss.

    :type: str, max length 1024
    """

    general_insomnia = db.Column(db.String(1024))
    """
    Client has insomnia.

    :type: str, max length 1024
    """

    general_other = db.Column(db.String(1024))
    """
    Client has other general problems.

    :type: str, max length 1024
    """

    blood_bloodpressure = db.Column(db.String(1024))
    """
    Client has high blood pressure.

    :type: str, max length 1024
    """

    blood_heartattack = db.Column(db.String(1024))
    """
    Client had a heart attack or myocardial infarction.

    :type: str, max length 1024
    """

    blood_heartdissease = db.Column(db.String(1024))
    """
    Client has a heart dissease.

    :type: str, max length 1024
    """

    blood_congestive = db.Column(db.String(1024))
    """
    Client has congestive heart failure.

    :type: str, max length 1024
    """

    blood_aneurysm = db.Column(db.String(1024))
    """
    Client has an aneurysm.

    :type: str, max length 1024
    """

    blood_bleeding = db.Column(db.String(1024))
    """
    Client has a bleeding disorder.

    :type: str, max length 1024
    """

    blood_bloodclots = db.Column(db.String(1024))
    """
    Client has blood cloths or deep vein trombosis.

    :type: str, max length 1024
    """

    blood_anemia = db.Column(db.String(1024))
    """
    Client has anemia.

    :type: str, max length 1024
    """

    blood_chestpain = db.Column(db.String(1024))
    """
    Client has chest pain or angina.

    :type: str, max length 1024
    """

    blood_arrythmia = db.Column(db.String(1024))
    """
    Client has arrythmia.

    :type: str, max length 1024
    """

    blood_cholesterol = db.Column(db.String(1024))
    """
    Client has high cholesterol.

    :type: str, max length 1024
    """

    blood_other = db.Column(db.String(1024))
    """
    Client has other cardiovascular problems.

    :type: str, max length 1024
    """

    digestive_irritablebowel = db.Column(db.String(1024))
    """
    Client has irritable bowel syndrome.

    :type: str, max length 1024
    """

    digestive_crohns = db.Column(db.String(1024))
    """
    Client has Crohn's disease.

    :type: str, max length 1024
    """

    digestive_celiac = db.Column(db.String(1024))
    """
    Client has Celiac disease.

    :type: str, max length 1024
    """

    digestive_reflux = db.Column(db.String(1024))
    """
    Client has Gastro-esophageal reflux or gastritis.

    :type: str, max length 1024
    """

    digestive_ulcer = db.Column(db.String(1024))
    """
    Client has an ulcer.

    :type: str, max length 1024
    """

    digestive_loosestool = db.Column(db.String(1024))
    """
    Client has frequent loose stools.

    :type: str, max length 1024
    """

    digestive_constipation = db.Column(db.String(1024))
    """
    Client has frequent constipation.

    :type: str, max length 1024
    """

    digestive_eatingdiscomfort = db.Column(db.String(1024))
    """
    Client has discomfort after meals.

    :type: str, max length 1024
    """

    digestive_hiatalhernia = db.Column(db.String(1024))
    """
    Client has a hiatal hernia.

    :type: str, max length 1024
    """

    digestive_swallowing = db.Column(db.String(1024))
    """
    Client has swallowing dysfunction.

    :type: str, max length 1024
    """

    digestive_liver = db.Column(db.String(1024))
    """
    Client has liver disorder.

    :type: str, max length 1024
    """

    digestive_other = db.Column(db.String(1024))
    """
    Client has an other digestive disorder.

    :type: str, max length 1024
    """

    skeletal_arthritis = db.Column(db.String(1024))
    """
    Client has osteo-arthritis.

    :type: str, max length 1024
    """

    skeletal_fractures = db.Column(db.String(1024))
    """
    Client has fractures.

    :type: str, max length 1024
    """

    skeletal_compressionfracture = db.Column(db.String(1024))
    """
    Client has a compression fracture.

    :type: str, max length 1024
    """

    skeletal_stressfracture = db.Column(db.String(1024))
    """
    Client has a stress fracture.

    :type: str, max length 1024
    """

    skeletal_dislocation = db.Column(db.String(1024))
    """
    Client has a dislocation.

    :type: str, max length 1024
    """

    skeletal_inguinalhernia = db.Column(db.String(1024))
    """
    Client has an inguinal hernia.

    :type: str, max length 1024
    """

    skeletal_otherhernia = db.Column(db.String(1024))
    """
    Client has an other hernia.

    :type: str, max length 1024
    """

    skeletal_diastatis = db.Column(db.String(1024))
    """
    Client has diastasis recti.

    :type: str, max length 1024
    """

    skeletal_carpaltunnel = db.Column(db.String(1024))
    """
    Client has carpal tunnel syndrome.

    :type: str, max length 1024
    """

    skeletal_thoracicoutlet = db.Column(db.String(1024))
    """
    Client has thoracic outlet syndrome.

    :type: str, max length 1024
    """

    skeletal_spinalstenosis = db.Column(db.String(1024))
    """
    Client has spinal stenosis.

    :type: str, max length 1024
    """

    skeletal_sciatica = db.Column(db.String(1024))
    """
    Client has sciatica.

    :type: str, max length 1024
    """

    skeletal_spondylolisthesis = db.Column(db.String(1024))
    """
    Client has spondylolisthesis.

    :type: str, max length 1024
    """

    skeletal_dischernia = db.Column(db.String(1024))
    """
    Client has a herniated disc.

    :type: str, max length 1024
    """

    skeletal_temporomandibular = db.Column(db.String(1024))
    """
    Client has temporomandibular disorder

    :type: str, max length 1024
    """

    skeletal_other = db.Column(db.String(1024))
    """
    Client has an other skeletal disorder.

    :type: str, max length 1024
    """

    immune_diabetes = db.Column(db.String(1024))
    """
    Client has diabetes.

    :type: str, max length 1024
    """

    immune_lowbloodsugar = db.Column(db.String(1024))
    """
    Client has low blood sugar.

    :type: str, max length 1024
    """

    immune_hepatitis = db.Column(db.String(1024))
    """
    Client has hepatitis.

    :type: str, max length 1024
    """

    immune_hiv = db.Column(db.String(1024))
    """
    Client has HIV/AIDS.

    :type: str, max length 1024
    """

    immune_tuberculosis = db.Column(db.String(1024))
    """
    Client has tuberculosis.

    :type: str, max length 1024
    """

    immune_cancer = db.Column(db.String(1024))
    """
    Client has cancer.

    :type: str, max length 1024
    """

    immune_thyroid = db.Column(db.String(1024))
    """
    Client has thyroid dysfunction.

    :type: str, max length 1024
    """

    immune_autoimmune = db.Column(db.String(1024))
    """
    Client has an autoimmune disease.

    :type: str, max length 1024
    """

    immune_osteoporosis = db.Column(db.String(1024))
    """
    Client has osteoporosis or osteopenia.

    :type: str, max length 1024
    """

    immune_gout = db.Column(db.String(1024))
    """
    Client has gout.

    :type: str, max length 1024
    """

    immune_rheuma = db.Column(db.String(1024))
    """
    Client has rheumatoid arthritis.

    :type: str, max length 1024
    """

    immune_lupus = db.Column(db.String(1024))
    """
    Client has lupus.

    :type: str, max length 1024
    """

    immune_fibromyalgia = db.Column(db.String(1024))
    """
    Client has fibromyalgia.

    :type: str, max length 1024
    """

    immune_other = db.Column(db.String(1024))
    """
    Client has an other immune condition.

    :type: str, max length 1024
    """

    surgery_bypass = db.Column(db.String(1024))
    """
    Client has had bypass or CABG surgery

    :type: str, max length 1024
    """

    surgery_pacemaker = db.Column(db.String(1024))
    """
    Client has a pacemaker or defibrilator.

    :type: str, max length 1024
    """

    surgery_stents = db.Column(db.String(1024))
    """
    Client has had vascular surgery or has stents.

    :type: str, max length 1024
    """

    surgery_abdominal = db.Column(db.String(1024))
    """
    Client has abdominal surgery.

    :type: str, max length 1024
    """

    surgery_gastric = db.Column(db.String(1024))
    """
    Client has gastric bypass surgery.

    :type: str, max length 1024
    """

    surgery_hysterectomy = db.Column(db.String(1024))
    """
    Client has had a hysterectomy.

    :type: str, max length 1024
    """

    surgery_tuballigation = db.Column(db.String(1024))
    """
    Client has had a tubal ligation.

    :type: str, max length 1024
    """

    surgery_laparoscopy = db.Column(db.String(1024))
    """
    Client has had a laparoscopy.

    :type: str, max length 1024
    """

    surgery_bladder = db.Column(db.String(1024))
    """
    Client has had a bladder surgery.

    :type: str, max length 1024
    """

    surgery_csection = db.Column(db.String(1024))
    """
    Client has had a C-section.

    :type: str, max length 1024
    """

    surgery_hernia = db.Column(db.String(1024))
    """
    Client has had hernia surgery.

    :type: str, max length 1024
    """

    surgery_gallbladder = db.Column(db.String(1024))
    """
    Client has had gallbladder surgery.

    :type: str, max length 1024
    """

    surgery_orthopedic = db.Column(db.String(1024))
    """
    Client has had orthopedic surgery.

    :type: str, max length 1024
    """

    surgery_back = db.Column(db.String(1024))
    """
    Client has had back or neck surgery.

    :type: str, max length 1024
    """

    surgery_plastic = db.Column(db.String(1024))
    """
    Client has had plastic surgery.

    :type: str, max length 1024
    """

    surgery_other = db.Column(db.String(1024))
    """
    Client has had an other form of surgery.

    :type: str, max length 1024
    """

    uro_urological = db.Column(db.String(1024))
    """
    Client has an urological disorder.

    :type: str, max length 1024
    """

    uro_kidney = db.Column(db.String(1024))
    """
    Client has a kidney disease.

    :type: str, max length 1024
    """

    uro_incontinence = db.Column(db.String(1024))
    """
    Client is incontinent.

    :type: str, max length 1024
    """

    uro_endometriosis = db.Column(db.String(1024))
    """
    Client has endometriosis.

    :type: str, max length 1024
    """

    uro_gynecology = db.Column(db.String(1024))
    """
    Client has an other gynecological disorder.

    :type: str, max length 1024
    """

    uro_fibroids = db.Column(db.String(1024))
    """
    Client has fibroids or cysts.

    :type: str, max length 1024
    """

    uro_childbirth = db.Column(db.String(1024))
    """
    Client has given birth.

    :type: str, max length 1024
    """

    uro_other = db.Column(db.String(1024))
    """
    Client has an other urogenital disorder.

    :type: str, max length 1024
    """

    respiratory_smoke = db.Column(db.String(1024))
    """
    Client smokes.

    :type: str, max length 1024
    """

    respiratory_asthma = db.Column(db.String(1024))
    """
    Client has asthma.

    :type: str, max length 1024
    """

    respiratory_emphysema = db.Column(db.String(1024))
    """
    Client has emphysema.

    :type: str, max length 1024
    """

    respiratory_pneumonia = db.Column(db.String(1024))
    """
    Client has pneumonia.

    :type: str, max length 1024
    """

    respiratory_allergies = db.Column(db.String(1024))
    """
    Client has respiratory allergies.

    :type: str, max length 1024
    """

    respiratory_sleepapnea = db.Column(db.String(1024))
    """
    Client has sleep apnea.

    :type: str, max length 1024
    """

    respiratory_deviatedseptum = db.Column(db.String(1024))
    """
    Client has a deviated septum.

    :type: str, max length 1024
    """

    respiratory_shortbreath = db.Column(db.String(1024))
    """
    Client has shortness of breath.

    :type: str, max length 1024
    """

    respiratory_other = db.Column(db.String(1024))
    """
    Client has an other respiratory disorder.

    :type: str, max length 1024
    """

    neuro_brain = db.Column(db.String(1024))
    """
    Client has had a head or brain injury.

    :type: str, max length 1024
    """

    neuro_stroke = db.Column(db.String(1024))
    """
    Client has had a stroke.

    :type: str, max length 1024
    """

    neuro_ms = db.Column(db.String(1024))
    """
    Client has multiple sclerosis.

    :type: str, max length 1024
    """

    neuro_neuropathy = db.Column(db.String(1024))
    """
    Client has peripheral neuropathy.

    :type: str, max length 1024
    """

    neuro_epilepsy = db.Column(db.String(1024))
    """
    Client has epilepsy or seizures.

    :type: str, max length 1024
    """

    neuro_parkinson = db.Column(db.String(1024))
    """
    Client has Parkinson's disease.

    :type: str, max length 1024
    """

    neuro_neuromuscular = db.Column(db.String(1024))
    """
    Client has a neuromuscular disorder.

    :type: str, max length 1024
    """

    neuro_other = db.Column(db.String(1024))
    """
    Client has an other neurological disorder.

    :type: str, max length 1024
    """

    trauma_whiplash = db.Column(db.String(1024))
    """
    Client has had a whiplash.

    :type: str, max length 1024
    """

    trauma_accident = db.Column(db.String(1024))
    """
    Client has been in a motor vehicle accident.

    :type: str, max length 1024
    """

    trauma_concussion = db.Column(db.String(1024))
    """
    Client has had a concussion.

    :type: str, max length 1024
    """

    trauma_other = db.Column(db.String(1024))
    """
    Client has had an other trauma.

    :type: str, max length 1024
    """

    nutrition_deficiency = db.Column(db.String(1024))
    """
    Client has a nutritional deficiency.

    :type: str, max length 1024
    """

    nutrition_allergies = db.Column(db.String(1024))
    """
    Client has nutritional allergies.

    :type: str, max length 1024
    """

    nutrition_eating = db.Column(db.String(1024))
    """
    Client has an eating disorder.

    :type: str, max length 1024
    """

    nutrition_other = db.Column(db.String(1024))
    """
    Client has an other nutritional disorder.

    :type: str, max length 1024
    """
