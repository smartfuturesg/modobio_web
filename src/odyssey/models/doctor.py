"""
Database tables for the doctor's portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'Medical'.
"""
from datetime import datetime

from odyssey.constants import DB_SERVER_TIME, BLOODTEST_EVAL
from odyssey import db

class MedicalImaging(db.Model):
    """ Medical Imaging table

    This table stores the medical imaging history of a client. 
    As long as the clientID exists, we can add images to this table and search by clientID
    """
    __tablename__ = 'MedicalImaging'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Index

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid', ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    image_date = db.Column(db.Date)
    """
    Date image was taken
    To be filled in by the doctor

    :type: :class:`datetime.date`
    """

    image_type = db.Column(db.String(1024))
    """
    Type of image, to be filled in by the doctor via a drop down menu
    Possible options are: Ultrasound, CT scan, X-Ray, MRI, PET scan.

    :type: str, max length 1024
    """
    
    image_read = db.Column(db.Text)
    """
    Text representing the doctors diagnosis or notes of the image

    :type: str
    """

    image_origin_location = db.Column(db.Text)
    """
    Name of and information about clinic where image was gathered.
    eg. SimonMed imaging, Banner imaging, etc.
    May include name, address and contact information of clinic.

    :type: str
    """
    
    image_path = db.Column(db.Text)
    """
    image S3 path

    :type: str
    """

    image_size = db.Column(db.Integer)
    """
    Size of image in bytes

    :type: int
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

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
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

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
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

class MedicalBloodTests(db.Model):
    """Holds information about client blood tests"""

    __tablename__ = "MedicalBloodTests"

    testid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique id identifying the test

    :type: int, primary key, auto incrementing
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid', ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key
    """

    date = db.Column(db.Date)
    """
    Date the test was administered

    :type: date
    """

    panel_type = db.Column(db.String, default="Nonroutine")
    """
    denotes the panel type of the test, null if not one of the "standard tests"

    :type: string
    """

    notes = db.Column(db.String)
    """
    doctor's notes about the test

    :type: string
    """

class MedicalBloodTestResultTypes(db.Model):
    """Holds a list of possible blood test result types(i.e. hemoglobulin, cholesterol, glucose, etc.)"""

    __tablename__ = "MedicalBloodTestResultTypes"

    resultid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    autoincrementing primary key

    :type: int, primary key, autoincrementing
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    result_name = db.Column(db.String)
    """
    name of the result

    :type: string
    """

    normal_min = db.Column(db.Float)
    """
    Minimum of normal range for blood test

    :type: float
    """
    normal_max = db.Column(db.Float)
    """
    Maximum of normal range for blood test

    :type: float
    """
    optimal_min = db.Column(db.Float)
    """
    Minimum of optimal range for blood test

    :type: float
    """
    optimal_max = db.Column(db.Float)
    """
    Maximum of optimal range for blood test

    :type: float
    """

    unit = db.Column(db.String)
    """
    Unit of reported blood test. 

    :type: str
    """

class MedicalBloodTestResults(db.Model):
    """Holds the results of a blood test identified by a blood test id"""

    __tablename__ = "MedicalBloodTestResults"

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    autoincrementing result idx

    :type: int, primary key, autoincrementing
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    timestamp for when object was created. DB server time is used. 

    :type: datetime
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    timestamp for when object was updated. DB server time is used. 

    :type: datetime
    """

    testid = db.Column(db.Integer, db.ForeignKey('MedicalBloodTests.testid', ondelete="CASCADE"), nullable=False)
    """
    foreign key to MedicalBloodTests.clientid

    :type: int, foreign key
    """

    resultid = db.Column(db.Integer, db.ForeignKey('MedicalBloodTestResultTypes.resultid', ondelete="CASCADE"), nullable=False)
    """
    foreign key to MedicalBloodTestResultTypes.resultid

    :type: int, foreign key
    """

    result_value = db.Column(db.Float)
    """
    numerical value of the parameter

    :type: int
    """

    evaluation = db.Column(db.String)
    """
    Evaluation of blood test result based on
    reccomended ranges for normal and optimal results
    possible values are: 'optimal','normal','abnormal'

    :type: str
    """

@db.event.listens_for(MedicalBloodTestResults, "after_insert")
def add_rest_result_eval(mapper, connection, target):
    """
    Listens for inserts into blood test result table.
    Runs evaluation on the DB side and stores the eval result.
    Evaluation is based of normal and optimal ranges of each blood test type
    """
    connection.execute(BLOODTEST_EVAL.format(target.idx, target.resultid, target.result_value))