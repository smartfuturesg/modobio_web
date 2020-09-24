"""
Database tables for the doctor's portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'Medical'.
"""
from datetime import datetime
from odyssey import db

class MedicalBloodChemistryCBC(db.Model):
    """ Client Blood Chemistry Complete Blood Count (CBC) table

    This table stores client's blood test CBC results
    """

    __tablename__ = 'MedicalBloodChemistryCBC'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='MedicalBloodChemistryCBC_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """
    
    exam_date = db.Column(db.Date)
    """
    Exam date.

    :type: datetime.date
    """
    
    rbc = db.Column(db.Float)
    """
    RBC/RCC level
    
    units: N/A
    :type: float
    """

    hemoglobin = db.Column(db.Float)
    """
    Hemoglobin level
    
    units: N/A
    :type: float
    """

    hematocrit = db.Column(db.Float)
    """
    Hematocrit level
    
    units: percent
    :type: float
    """

    mcv = db.Column(db.Float)
    """
    MCV level
    
    units: fL
    :type: float
    """

    mch = db.Column(db.Float)
    """
    MCH level
    
    units: pg
    :type: float
    """

    mchc = db.Column(db.Float)
    """
    MCHC level
    
    units: g/dL
    :type: float
    """

    rdw = db.Column(db.Float)
    """
    RDW level
    
    units: percent
    :type: float
    """

    wbc = db.Column(db.Float)
    """
    WBC/WCC level
    
    units: x10E3/uL
    :type: float
    """

    rel_neutrophils = db.Column(db.Float)
    """
    Relative Neutrophils
    
    units: percent
    :type: float
    """

    abs_neutrophils = db.Column(db.Float)
    """
    Absolute Neutrophils level
    
    units: x10E3/uL
    :type: float
    """

    rel_lymphocytes = db.Column(db.Float)
    """
    Relative Lymphocytes
    
    units: percent
    :type: float
    """

    abs_lymphocytes = db.Column(db.Float)
    """
    Absolute Lymphocytes
    
    units: x10E3/uL
    :type: float
    """

    rel_monocytes = db.Column(db.Float)
    """
    Relative Monocytes
    
    units: U/L
    :type: float
    """

    abs_monocytes = db.Column(db.Float)
    """
    Absolute Monocytes
    
    units: x10E3/uL
    :type: float
    """

    rel_eosinophils = db.Column(db.Float)
    """
    Relative Eosinophils
    
    units: percent
    :type: float
    """

    abs_eosinophils = db.Column(db.Float)
    """
    Absolute Eosinophils
    
    units: x10E3/uL
    :type: float
    """

    basophils = db.Column(db.Float)
    """
    Basophils level
    
    units: percent
    :type: float
    """

    platelets = db.Column(db.Float)
    """
    Platelets
    
    units: x10E3/mm^3
    :type: float
    """

    plateletsByMch = db.Column(db.Float)
    """
    Platelets/MCH
    
    units: N/A
    :type: float
    """   
    
    plateletsByLymphocyte = db.Column(db.Float)
    """
    Platelets/Lymphocyte
    
    units: N/A
    :type: float
    """   

    neutrophilByLymphocyte = db.Column(db.Float)
    """
    Neutrophil/Lymphocyte
    
    units: N/A
    :type: float
    """   

    lymphocyteByMonocyte = db.Column(db.Float)
    """
    Lymphocyte/Monocyte
    
    units: N/A
    :type: float
    """   

class MedicalBloodChemistryCMP(db.Model):
    """ Client Blood Chemistry Comprehensive Metabolic Panel (CMP) table

    This table stores client's blood test CMP results
    """

    __tablename__ = 'MedicalBloodChemistryCMP'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='MedicalBloodChemistryCMP_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """
    
    exam_date = db.Column(db.Date)
    """
    Exam date.

    :type: datetime.date
    """
    
    glucose = db.Column(db.Float)
    """
    Glucose level
    
    units: mg/dL
    :type: float
    """

    sodium = db.Column(db.Float)
    """
    Sodium level
    
    units: mmol/L
    :type: float
    """

    potassium = db.Column(db.Float)
    """
    Potassium level
    
    units: mmol/L
    :type: float
    """

    carbon_dioxide = db.Column(db.Float)
    """
    Carbon Dioxide level
    
    units: mmol/L
    :type: float
    """

    chloride = db.Column(db.Float)
    """
    Chloride level
    
    units: mmol/L
    :type: float
    """

    magnesium = db.Column(db.Float)
    """
    Magnesium level
    
    units: mg/dL
    :type: float
    """

    calcium = db.Column(db.Float)
    """
    Calcium level
    
    units: mg/dL
    :type: float
    """

    phosphorus = db.Column(db.Float)
    """
    Phosphorus level
    
    units: mg/dL
    :type: float
    """

    uric_acid = db.Column(db.Float)
    """
    Utic Acid level
    
    units: mg/dL
    :type: float
    """

    bun = db.Column(db.Float)
    """
    bun level
    
    units: mg/dL
    :type: float
    """

    creatinine = db.Column(db.Float)
    """
    creatinine level
    
    units: mg/dL
    :type: float
    """

    ast = db.Column(db.Float)
    """
    AST level
    
    units: U/L
    :type: float
    """

    alt = db.Column(db.Float)
    """
    ALT level
    
    units: U/L
    :type: float
    """

    alk_phophatase = db.Column(db.Float)
    """
    Alkaline Phosphatase level
    
    units: U/L
    :type: float
    """

    bilirubin = db.Column(db.Float)
    """
    Total bilirubin level
    
    units: mg/dL
    :type: float
    """

    protein = db.Column(db.Float)
    """
    Protein level
    
    units: g/dL
    :type: float
    """

    albumin = db.Column(db.Float)
    """
    Albumin level
    
    units: g/dL
    :type: float
    """

    globulin = db.Column(db.Float)
    """
    Globulin level
    
    units: g/dL
    :type: float
    """

    bunByAlbumin = db.Column(db.Float)
    """
    BUN/Albumnin Ratio
    
    units: N/A
    :type: float
    """    

class MedicalHistory(db.Model):
    """ Medical history table

    This table stores the medical history of a client. The information is taken
    only once, during the initial consult.
    """
    __tablename__ = 'MedicalHistory'

    displayname = 'Medical History'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Index

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='MedicalHistory_clientid_fkey', ondelete="CASCADE"), nullable=False)
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


class MedicalPhysicalExam(db.Model):
    """ Medical physical exam table

    This table stores the results of the physical exam of a client. The
    information is taken only once, during the initial consult.
    """
    __tablename__ = 'MedicalPhysicalExam'

    displayname = 'Medical Physical Examination'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Index

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='MedicalPhysicalExam_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    timestamp = db.Column(db.DateTime)
    """
    Timestamp of the assessment.

    :type: datetime.datetime, primary key
    """
    
    vital_heartrate = db.Column(db.Integer)
    """
    Resting heart rate
    
    :type: int
    :unit: bpm
    """

    vital_respiratoryrate = db.Column(db.Integer)
    """
    Respiratory rate

    :type: int
    :unit: breaths per minute
    """

    vital_systolic = db.Column(db.Integer)
    """
    Systolic blood pressure

    :type: int
    :unit: mm Hg
    """

    vital_diastolic = db.Column(db.Integer)
    """
    Diastolic blood pressure

    :type: int
    :unit: mm Hg
    """

    vital_temperature = db.Column(db.Float)
    """
    Body temperature

    :type: float
    :unit: Fahrenheit
    """

    vital_weight = db.Column(db.Float)
    """
    Body weight

    :type: float
    :unit: lbs
    """

    vital_height = db.Column(db.String(20))
    """
    Body height

    Stored as a string until we figure out how to convert ft+in to a single number.

    :type: str, max length 20
    :unit: TBD
    """


    vital_height_inches = db.Column(db.Float)
    """
    Body height

    Height in inches

    :type: float
    :unit: inches
    """

    cardiac_rrr = db.Column(db.Boolean)
    """
    "Regular rate and rhythm" heart sound

    :type: bool
    """

    cardiac_s1s2 = db.Column(db.Boolean)
    """
    S1 or S2 type heart sounds

    :type: bool
    """

    cardiac_murmurs = db.Column(db.Boolean)
    """
    Murmurs in heart sounds

    :type: bool
    """

    cardiac_murmurs_info = db.Column(db.String(1024))
    """
    Specific details regarding heart murmurs

    :type: str, max length 1024
    """

    cardiac_rubs = db.Column(db.Boolean)
    """
    Rubs in heart sounds

    :type: bool
    """

    cardiac_gallops = db.Column(db.Boolean)
    """
    Gallops in heart sounds

    :type: bool
    """

    pulmonary_clear = db.Column(db.Boolean)
    """
    Clear lung sounds

    :type: bool
    """

    pulmonary_wheezing = db.Column(db.Boolean)
    """
    Wheezing in lung sounds

    :type: bool
    """

    pulmonary_wheezing_info = db.Column(db.String(1024))
    """
    Specific details regarding wheezing in lung sounds

    :type: str, max length 1024
    """

    pulmonary_rales = db.Column(db.Boolean)
    """
    Rales in lung sounds

    :type: bool
    """

    pulmonary_rhonchi = db.Column(db.Boolean)
    """
    Rhonchi in lung sounds

    :type: bool
    """

    abdominal_soft = db.Column(db.Boolean)
    """
    Soft abdomen

    :type: bool
    """

    abdominal_hard = db.Column(db.Boolean)
    """
    Non tender abdomen

    :type: bool
    """

    abdominal_bowel = db.Column(db.Boolean)
    """
    Positive bowel sounds

    :type: bool
    """

    abdominal_hsm = db.Column(db.Boolean)
    """
    Hepatosplenomegaly, enlarged liver and/or spleen

    :type: bool
    """

    abdominal_hsm_info = db.Column(db.String(1024))
    """
    Specific details regarding hepatosplenomegaly, enlarged liver and/or spleen

    :type: bool
    """

    notes = db.Column(db.Text)
    """
    General notes during physical examination.

    :type: str
    """

class MedicalBloodChemistryLipids(db.Model):
    """ Blood Test - Lipid results

    This table stores the blood test - lipids results of clients.
    """
    __tablename__ = 'MedicalBloodChemistryLipids'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Index

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='BloodLipids_clientid_fkey', ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    exam_date = db.Column(db.Date)
    """
    Date blood test was administered.

    :type: :class:`datetime.date`
    """

    cholesterol_total = db.Column(db.Float)
    """
    Cholesterol total

    :type: Integer
    :unit: mg/dL
    """

    cholesterol_ldl = db.Column(db.Float)
    """
    Cholesterol ldl

    :type: Integer
    :unit: mg/dL
    """

    cholesterol_hdl = db.Column(db.Float)
    """
    Cholesterol hdl

    :type: Integer
    :unit: mg/dL
    """

    triglycerides = db.Column(db.Float)
    """
    Triglycerides

    :type: Integer
    :unit: mg/dL
    """

    #calculated values
    cholesterol_over_hdl = db.Column(db.Float)
    """
    cholesterol total / cholesterol hdl

    :type: float
    :unit: #
    """

    triglycerides_over_hdl = db.Column(db.Float)
    """
    triglycerides / hdl

    :type: float
    :unit: #
    """

    ldl_over_hdl = db.Column(db.Float)
    """
    cholesterol ldl / cholesterol hdl

    :type: float
    :unit: #
    """

class MedicalBloodChemistryThyroid(db.Model):
    """ Blood Test - Thyroid results

    This table stores the blood test - thyroid results of clients.
    """
    __tablename__ = 'MedicalBloodChemistryThyroid'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Index

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='BloodThyroid_clientid_fkey', ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    exam_date = db.Column(db.Date)
    """
    Date blood test was administered.

    :type: :class:`datetime.date`
    """

    t3_resin_uptake = db.Column(db.Integer)
    """
    T3 Resin Uptake(%)

    :type: integer
    :units: %
    """

    thyroglobulin = db.Column(db.Integer)
    """
    Thyroglobulin, serum

    :type: integer
    :units: ng/mL
    """

    thyroidial_iodine_uptake = db.Column(db.Integer)
    """
    Thyroidal Iodine Uptake (I-123)

    :type: integer
    :units: %
    """

    tsh = db.Column(db.Float)
    """
    Thyroid-stimulating hormone(TSH), serum

    :type: float
    :units: μU/mL
    """

    tsi = db.Column(db.Integer)
    """
    Thyroid-stimulating immunoglobulin(TSI)

    :type: integer
    :units: %
    """

    thyroxine_binding_globulin = db.Column(db.Integer)
    """
    Thyroxine-binding globulin, serum

    :type: integer
    :units: μg/mL
    """

    thyroxine_index = db.Column(db.Integer)
    """
    Thyroxine index, free (estimate)

    :type: integer
    :units: #
    """

    t4_serum_total = db.Column(db.Integer)
    """
    Thyroxine (T4), serum total

    :type: integer
    :units: μg/dL
    """

    t4_serum_free = db.Column(db.Float)
    """
    Thyroxine (T4), serum free

    :type: float
    :units: ng/dL
    """

    t3_serum_total = db.Column(db.Integer)
    """
    Triiodothyronine (T3), serum total

    :type: integer
    :units: ng/dL
    """

    t3_serum_reverse = db.Column(db.Integer)
    """
    Triiodothyronine (T3), serum reverse

    :type: integer
    :units: ng/dL
    """

    t3_serum_free = db.Column(db.Float)
    """
    Triiodothyronine (T3), serum free

    :type: integer
    :units: pg/mL
    """

class MedicalBloodChemistryA1C(db.Model):
    """ Blood Test - A1C results

    This table stores the blood test - thyroid results of clients.
    """
    __tablename__ = 'MedicalBloodChemistryA1C'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Index

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='BloodA1C_clientid_fkey', ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    exam_date = db.Column(db.Date)
    """
    Date blood test was administered.

    :type: :class:`datetime.date`
    """

    a1c = db.Column(db.Float)
    """
    Hemoglobin A1C

    :type: float
    :units: %
    """    