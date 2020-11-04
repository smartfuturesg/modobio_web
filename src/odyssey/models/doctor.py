"""
Database tables for the doctor's portion of the Modo Bio Staff application.
All tables in this module are prefixed with ``Medical``.
"""
from datetime import datetime

from odyssey.constants import DB_SERVER_TIME, BLOODTEST_EVAL
from odyssey import db

class MedicalImaging(db.Model):
    """ Medical Imaging table.

    A table to store information about uploaded medical images.
    """
    __tablename__ = 'MedicalImaging'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid', ondelete="CASCADE"), nullable=False)
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid <odyssey.models.client.ClientInfo.clientid>`
    """

    reporter_id = db.Column(db.Integer, nullable=False)
    #TODO: convert this to refer back to userid as a foreign key
    """
    Staff id of the reporting staff member. Should be a staff with the role of 'doc' or 'docext'. 

    :type: int
    """

    image_date = db.Column(db.Date)
    """
    Date when image was taken.

    :type: :class:`datetime.date`
    """

    image_type = db.Column(db.String(1024))
    """
    Image type.

    Describes the imaging technique used to create the image. Options are:

    - CT
    - MRI
    - PET
    - Scopes
    - Special imaging
    - Ultrasound
    - X-ray

    :type: str, max length 1024
    """
    
    image_read = db.Column(db.Text)
    """
    Doctor's diagnosis or notes of the image.

    :type: str
    """

    image_origin_location = db.Column(db.Text)
    """
    Where was image created.

    Name and address of clinic where image was gathered.

    :type: str
    """
    
    image_path = db.Column(db.Text)
    """
    Path where image is stored.

    In development mode, it is a path on the local filesystem. In production
    it is a path in an AWS S3 bucket.

    :type: str
    """

    image_size = db.Column(db.Integer)
    """
    Size of image in bytes.

    :type: int
    """


class MedicalHistory(db.Model):
    """ Medical history table.

    This table stores the medical history of a client. The information is taken
    only once, during the initial consult.
    """
    __tablename__ = 'MedicalHistory'

    displayname = 'Medical history'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='MedicalHistory_clientid_fkey', ondelete="CASCADE"), nullable=False)
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid <odyssey.models.client.ClientInfo.clientid>`
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
    """ Medical physical exam table.

    This table stores the results of the physical exam of a client. The
    information is taken only once, during the initial consult.
    """
    __tablename__ = 'MedicalPhysicalExam'

    displayname = 'Medical physical examination'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='MedicalPhysicalExam_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid <odyssey.models.client.ClientInfo.clientid>`
    """

    reporter_id = db.Column(db.Integer, nullable=False)
    #TODO: convert this to refer back to userid as a foreign key
    """
    Staff id of the reporting staff member. Should be a staff with the role of 'doc' or 'docext'. 

    :type: int
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Timestamp of the assessment.

    :type: :class:`datetime.datetime`, primary key
    """
    
    vital_heartrate = db.Column(db.Integer)
    """
    Resting heart rate.
    
    :type: int
    :unit: bpm
    """

    vital_respiratoryrate = db.Column(db.Integer)
    """
    Respiratory rate.

    :type: int
    :unit: breaths per minute
    """

    vital_systolic = db.Column(db.Integer)
    """
    Systolic blood pressure.

    :type: int
    :unit: mmHg
    """

    vital_diastolic = db.Column(db.Integer)
    """
    Diastolic blood pressure.

    :type: int
    :unit: mmHg
    """

    vital_temperature = db.Column(db.Float)
    """
    Body temperature.

    :type: float
    :unit: Fahrenheit
    """

    vital_weight = db.Column(db.Float)
    """
    Body weight.

    :type: float
    :unit: lb
    """

    vital_height = db.Column(db.String(20))
    """
    Body height.

    Stored as a string until we figure out how to convert ft+in to a single number.

    :type: str, max length 20
    :unit: TBD
    """


    vital_height_inches = db.Column(db.Float)
    """
    Body height.

    :type: float
    :unit: inches
    """

    cardiac_rrr = db.Column(db.Boolean)
    """
    "Regular rate and rhythm" heart sound.

    :type: bool
    """

    cardiac_s1s2 = db.Column(db.Boolean)
    """
    S1 or S2 type heart sounds.

    :type: bool
    """

    cardiac_murmurs = db.Column(db.Boolean)
    """
    Murmurs in heart sounds.

    :type: bool
    """

    cardiac_murmurs_info = db.Column(db.String(1024))
    """
    Specific details regarding heart murmurs.

    :type: str, max length 1024
    """

    cardiac_rubs = db.Column(db.Boolean)
    """
    Rubs in heart sounds.

    :type: bool
    """

    cardiac_gallops = db.Column(db.Boolean)
    """
    Gallops in heart sounds.

    :type: bool
    """

    pulmonary_clear = db.Column(db.Boolean)
    """
    Clear lung sounds.

    :type: bool
    """

    pulmonary_wheezing = db.Column(db.Boolean)
    """
    Wheezing in lung sounds.

    :type: bool
    """

    pulmonary_wheezing_info = db.Column(db.String(1024))
    """
    Specific details regarding wheezing in lung sounds.

    :type: str, max length 1024
    """

    pulmonary_rales = db.Column(db.Boolean)
    """
    Rales in lung sounds.

    :type: bool
    """

    pulmonary_rhonchi = db.Column(db.Boolean)
    """
    Rhonchi in lung sounds.

    :type: bool
    """

    abdominal_soft = db.Column(db.Boolean)
    """
    Soft abdomen.

    :type: bool
    """

    abdominal_hard = db.Column(db.Boolean)
    """
    Non tender abdomen.

    :type: bool
    """

    abdominal_bowel = db.Column(db.Boolean)
    """
    Positive bowel sounds.

    :type: bool
    """

    abdominal_hsm = db.Column(db.Boolean)
    """
    Hepatosplenomegaly, enlarged liver and/or spleen.

    :type: bool
    """

    abdominal_hsm_info = db.Column(db.String(1024))
    """
    Specific details regarding hepatosplenomegaly, enlarged liver and/or spleen.

    :type: str, max length 1024
    """

    notes = db.Column(db.Text)
    """
    General notes during physical examination.

    :type: str
    """


class MedicalBloodTests(db.Model):
    """ Blood test table.

    This table stores metadata for blood tests.
    """

    __tablename__ = 'MedicalBloodTests'

    testid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique ID number identifying the test.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid', ondelete="CASCADE"), nullable=False)
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid <odyssey.models.client.ClientInfo.clientid>`
    """

    reporter_id = db.Column(db.Integer, nullable=False)
    #TODO: convert this to refer back to userid as a foreign key
    """
    Staff id of the reporting staff member. Should be a staff with the role of 'doc' or 'docext'. 

    :type: int
    """

    date = db.Column(db.Date)
    """
    Date the test was administered.

    :type: :class:`datetime.date`
    """

    panel_type = db.Column(db.String, default="Nonroutine")
    """
    Which panel does test belong to. ``None`` if not one of the standard tests.

    :type: str
    """

    notes = db.Column(db.String)
    """
    Notes regarding blood test.

    :type: str
    """


class MedicalBloodTestResultTypes(db.Model):
    """ Blood test evaluation limits.

    Blood test values can be evaluated as lying in "normal" or "optimal"
    ranges. What constitutes as a normal or optimal range depends on gender
    and possibly other factors. The range limits are calculated for each
    client and stored in this table.
    """

    __tablename__ = "MedicalBloodTestResultTypes"

    resultid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique ID number identifying the results.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    result_name = db.Column(db.String)
    """
    ??? What name? Panel? Client? Any random name made up by doctor?

    :type: str
    """

    normal_min = db.Column(db.Float)
    """
    Minimum of normal range for blood test.

    :type: float
    """

    normal_max = db.Column(db.Float)
    """
    Maximum of normal range for blood test.

    :type: float
    """

    optimal_min = db.Column(db.Float)
    """
    Minimum of optimal range for blood test.

    :type: float
    """

    optimal_max = db.Column(db.Float)
    """
    Maximum of optimal range for blood test.

    :type: float
    """

    unit = db.Column(db.String)
    """
    Measurement unit of the blood test.

    :type: str
    """

    panel = db.Column(db.String)
    """
    Which panel does result belong to. ``None`` if not one of the standard tests.

    :type: str
    """


class MedicalBloodTestResults(db.Model):
    """ Blood test result data.

    This table holds the value of a single blood test and the
    evaluation of that value given the normal and optimal ranges
    stored in :class:`MedicalBloodTestResultTypes`.
    """

    __tablename__ = "MedicalBloodTestResults"

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    testid = db.Column(db.Integer, db.ForeignKey('MedicalBloodTests.testid', ondelete="CASCADE"), nullable=False)
    """
    Unique test ID number.

    :type: int, foreign key to :attr:`MedicalBloodTests.testid`
    """

    resultid = db.Column(db.Integer, db.ForeignKey('MedicalBloodTestResultTypes.resultid', ondelete="CASCADE"), nullable=False)
    """
    Unique result ID number.

    :type: int, foreign key to :attr:`MedicalBloodTestResultTypes.resultid`
    """

    result_value = db.Column(db.Float)
    """
    Numerical value of the test result.

    :type: float
    """

    evaluation = db.Column(db.String)
    """
    Evaluation of blood test result based on recommended ranges for normal
    and optimal results. Possible values are:

    - optimal
    - normal
    - abnormal

    :type: str
    """


@db.event.listens_for(MedicalBloodTestResults, "after_insert")
def add_rest_result_eval(mapper, connection, target):
    """
    Event listener for the :class:`MedicalBloodTestResults` table.

    Listens for inserts into the :class:`MedicalBloodTestResults` table. When
    called, it runs the value evaluation on the DB side
    (:const:`odyssey.constants.BLOODTEST_EVAL`) and stores the result.
    Evaluation is based of normal and optimal ranges of each blood test type.

    Parameters
    ----------
    mapper : ???
        What does this do? Not used.

    connection : :class:`sqlalchemy.engine.Connection`
        Connection to the database engine.

    target : :class:`sqlalchemy.schema.Table`
        Target SQLAlchemy table, fixed to :class:`MedicalBloodTestResults` by decorator.
    """
    connection.execute(BLOODTEST_EVAL.format(target.idx, target.resultid, target.result_value))
