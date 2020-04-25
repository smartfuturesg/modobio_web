from odyssey import db


class Staff(db.Model):
    __tablename__ = 'Staff'

    staffid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(128))


class ClientInfo(db.Model):

    __tablename__ = 'ClientInfo'

    clientid = db.Column(db.Integer, primary_key=True, autoincrement=True)

    firstname = db.Column(db.String(50))
    middlename = db.Column(db.String(50))
    lastname = db.Column(db.String(50))

    street = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(10))
    country = db.Column(db.String(2))

    gender = db.Column(db.String(1))
    dob = db.Column(db.Date)

    email = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    # Should be an Enum
    preferred = db.Column(db.SmallInteger)

    emergency_contact = db.Column(db.String(50))
    emergency_phone = db.Column(db.String(20))

    healthcare_contact = db.Column(db.String(50))
    healthcare_phone = db.Column(db.String(20))


class ClientConsent(db.Model):
    
    __tablename__ = 'ClientConsent'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)

    infectious_disease = db.Column(db.Boolean)
    fullname = db.Column(db.String(100))
    signature = db.Column(db.Text)
    signdate = db.Column(db.Date)


class MedicalHistory(db.Model):

    __tablename__ = 'MedicalHistory'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)

    last_examination_date = db.Column(db.Date)
    last_examination_reason = db.Column(db.String(1024))

    goals = db.Column(db.Text)
    concerns = db.Column(db.Text)
    family_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    medication = db.Column(db.Text)

    diagnostic_xray = db.Column(db.String(1024))
    diagnostic_ctscan = db.Column(db.String(1024))
    diagnostic_endoscopy = db.Column(db.String(1024))
    diagnostic_mri = db.Column(db.String(1024))
    diagnostic_ultrasound = db.Column(db.String(1024))
    diagnostic_other = db.Column(db.String(1024))

    general_headaches = db.Column(db.String(1024))
    general_blackouts = db.Column(db.String(1024))
    general_vertigo = db.Column(db.String(1024))
    general_sinus = db.Column(db.String(1024))
    general_falling = db.Column(db.String(1024))
    general_balance = db.Column(db.String(1024))
    general_vision = db.Column(db.String(1024))
    general_hearing = db.Column(db.String(1024))
    general_memory = db.Column(db.String(1024))
    general_insomnia = db.Column(db.String(1024))
    general_other = db.Column(db.String(1024))

    blood_bloodpressure = db.Column(db.String(1024))
    blood_heartattack = db.Column(db.String(1024))
    blood_heartdissease = db.Column(db.String(1024))
    blood_congestive = db.Column(db.String(1024))
    blood_aneurysm = db.Column(db.String(1024))
    blood_bleeding = db.Column(db.String(1024))
    blood_bloodclots = db.Column(db.String(1024))
    blood_anemia = db.Column(db.String(1024))
    blood_chestpain = db.Column(db.String(1024))
    blood_arrythmia = db.Column(db.String(1024))
    blood_cholesterol = db.Column(db.String(1024))
    blood_other = db.Column(db.String(1024))

    digestive_irritablebowel = db.Column(db.String(1024))
    digestive_crohns = db.Column(db.String(1024))
    digestive_celiac = db.Column(db.String(1024))
    digestive_reflux = db.Column(db.String(1024))
    digestive_ulcer = db.Column(db.String(1024))
    digestive_loosestool = db.Column(db.String(1024))
    digestive_constipation = db.Column(db.String(1024))
    digestive_eatingdiscomfort = db.Column(db.String(1024))
    digestive_hiatalhernia = db.Column(db.String(1024))
    digestive_swallowing = db.Column(db.String(1024))
    digestive_liver = db.Column(db.String(1024))
    digestive_other = db.Column(db.String(1024))

    skeletal_arthritis = db.Column(db.String(1024))
    skeletal_fractures = db.Column(db.String(1024))
    skeletal_compressionfracture = db.Column(db.String(1024))
    skeletal_stressfracture = db.Column(db.String(1024))
    skeletal_dislocation = db.Column(db.String(1024))
    skeletal_inguinalhernia = db.Column(db.String(1024))
    skeletal_otherhernia = db.Column(db.String(1024))
    skeletal_diastatis = db.Column(db.String(1024))
    skeletal_carpaltunnel = db.Column(db.String(1024))
    skeletal_thoracicoutlet = db.Column(db.String(1024))
    skeletal_spinalstenosis = db.Column(db.String(1024))
    skeletal_sciatica = db.Column(db.String(1024))
    skeletal_spondylolisthesis = db.Column(db.String(1024))
    skeletal_dischernia = db.Column(db.String(1024))
    skeletal_temporomandibular = db.Column(db.String(1024))
    skeletal_other = db.Column(db.String(1024))

    immune_diabetes = db.Column(db.String(1024))
    immune_lowbloodsugar = db.Column(db.String(1024))
    immune_hepatitis = db.Column(db.String(1024))
    immune_hiv = db.Column(db.String(1024))
    immune_tuberculosis = db.Column(db.String(1024))
    immune_cancer = db.Column(db.String(1024))
    immune_thyroid = db.Column(db.String(1024))
    immune_autoimmune = db.Column(db.String(1024))
    immune_osteoporosis = db.Column(db.String(1024))
    immune_gout = db.Column(db.String(1024))
    immune_rheuma = db.Column(db.String(1024))
    immune_lupus = db.Column(db.String(1024))
    immune_fibromyalgia = db.Column(db.String(1024))
    immune_other = db.Column(db.String(1024))

    surgery_bypass = db.Column(db.String(1024))
    surgery_pacemaker = db.Column(db.String(1024))
    surgery_stents = db.Column(db.String(1024))
    surgery_abdominal = db.Column(db.String(1024))
    surgery_gastric = db.Column(db.String(1024))
    surgery_hysterectomy = db.Column(db.String(1024))
    surgery_tuballigation = db.Column(db.String(1024))
    surgery_laparoscopy = db.Column(db.String(1024))
    surgery_bladder = db.Column(db.String(1024))
    surgery_csection = db.Column(db.String(1024))
    surgery_hernia = db.Column(db.String(1024))
    surgery_galbladder = db.Column(db.String(1024))
    surgery_orthopedic = db.Column(db.String(1024))
    surgery_back = db.Column(db.String(1024))
    surgery_plastic = db.Column(db.String(1024))
    surgery_other = db.Column(db.String(1024))

    uro_urological = db.Column(db.String(1024))
    uro_kidney = db.Column(db.String(1024))
    uro_incontinence = db.Column(db.String(1024))
    uro_endometriosis = db.Column(db.String(1024))
    uro_gynecology = db.Column(db.String(1024))
    uro_fibroids = db.Column(db.String(1024))
    uro_childbirth = db.Column(db.String(1024))
    uro_other = db.Column(db.String(1024))

    respiratory_smoke = db.Column(db.String(1024))
    respiratory_asthma = db.Column(db.String(1024))
    respiratory_emphysema = db.Column(db.String(1024))
    respiratory_pneumonia = db.Column(db.String(1024))
    respiratory_allergies = db.Column(db.String(1024))
    respiratory_sleepapnea = db.Column(db.String(1024))
    respiratory_deviatedseptum = db.Column(db.String(1024))
    respiratory_shortbreath = db.Column(db.String(1024))
    respiratory_other = db.Column(db.String(1024))

    neuro_brain = db.Column(db.String(1024))
    neuro_stroke = db.Column(db.String(1024))
    neuro_ms = db.Column(db.String(1024))
    neuro_neuropathy = db.Column(db.String(1024))
    neuro_epilepsy = db.Column(db.String(1024))
    neuro_parkinson = db.Column(db.String(1024))
    neuro_neuromuscular = db.Column(db.String(1024))
    neuro_other = db.Column(db.String(1024))

    trauma_whiplash = db.Column(db.String(1024))
    trauma_accident = db.Column(db.String(1024))
    trauma_concussion = db.Column(db.String(1024))
    trauma_other = db.Column(db.String(1024))

    nutrition_deficiency = db.Column(db.String(1024))
    nutrition_allergies = db.Column(db.String(1024))
    nutrition_eating = db.Column(db.String(1024))
    nutrition_other = db.Column(db.String(1024))


class PTHistory(db.Model):

    __tablename__ = 'PTHistory'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)

    exercise = db.Column(db.Text)

    treatment = db.Column(db.String(1024))

    pain_areas = db.Column(db.Text)
    best_pain = db.Column(db.Integer)
    worst_pain = db.Column(db.Integer)
    current_pain = db.Column(db.Integer)
    makes_worse = db.Column(db.String(1024))
    makes_better = db.Column(db.String(1024))


class MobilityAssessment(db.Model):

    __tablename__ = 'MobilityAssessment'

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'),
                        nullable=False, primary_key=True)
    timestamp = db.Column(db.DateTime, primary_key=True)

    isa_left = db.Column(db.Integer)
    isa_right = db.Column(db.Integer)
    isa_dynamic = db.Column(db.Boolean)

    left_shoulder_er = db.Column(db.Integer)
    left_shoulder_ir = db.Column(db.Integer)
    left_shoulder_abd = db.Column(db.Integer)
    left_shoulder_add = db.Column(db.Integer)
    left_shoulder_flexion = db.Column(db.Integer)
    left_shoulder_extension = db.Column(db.Integer)

    right_shoulder_er = db.Column(db.Integer)
    right_shoulder_ir = db.Column(db.Integer)
    right_shoulder_abd = db.Column(db.Integer)
    right_shoulder_add = db.Column(db.Integer)
    right_shoulder_flexion = db.Column(db.Integer)
    right_shoulder_extension = db.Column(db.Integer)

    left_hip_er = db.Column(db.Integer)
    left_hip_ir = db.Column(db.Integer)
    left_hip_abd = db.Column(db.Integer)
    left_hip_add = db.Column(db.Integer)
    left_hip_flexion = db.Column(db.Integer)
    left_hip_extension = db.Column(db.Integer)

    right_hip_er = db.Column(db.Integer)
    right_hip_ir = db.Column(db.Integer)
    right_hip_abd = db.Column(db.Integer)
    right_hip_add = db.Column(db.Integer)
    right_hip_flexion = db.Column(db.Integer)
    right_hip_extension = db.Column(db.Integer)


db.create_all()
