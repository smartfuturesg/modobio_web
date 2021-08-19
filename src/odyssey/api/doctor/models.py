"""
Database tables for the doctor's portion of the Modo Bio Staff application.
All tables in this module are prefixed with ``Medical``.
"""
from sqlalchemy import text

from odyssey.utils.constants import DB_SERVER_TIME, BLOODTEST_EVAL
from odyssey import db
from odyssey.utils.base.models import BaseModel, BaseModelWithIdx, UserIdFkeyMixin, ReporterIdFkeyMixin

class MedicalBloodPressures(BaseModelWithIdx, UserIdFkeyMixin, ReporterIdFkeyMixin):
    """ Blood Pressure Table
    
    This table is used for storing the client's blood pressures.
    """    

    systolic = db.Column(db.Float)
    """
    Systolic value with units mmHg

    :type: float
    """

    diastolic = db.Column(db.Float)
    """
    Diastolic value with units mmHg

    :type: float
    """

    datetime_taken = db.Column(db.String)
    """
    The date and time the blood pressure levels were taken

    :type: :class: str
    """

class MedicalLookUpBloodPressureRange(BaseModelWithIdx):
    """ Medical Look Up Blood Pressure Ranges

    This table will store the blood pressure categories
    and ranges.

    Chart found from heart.org/bplevels
    """

    category = db.Column(db.String)
    """
    Blood Pressure Category

    :type: str
    """
    
    systolic = db.Column(db.String)
    """
    Systolic mmHg is the upper number for the range

    :type: str
    """

    and_or = db.Column(db.String)
    """
    and_or represents the union between systolic and diastolic
    numbers

    :type: str
    """

    diastolic = db.Column(db.String)
    """
    Diastolic mmHg is the lower number for the range

    :type: str
    """


class MedicalLookUpSTD(BaseModel):
    """ Medical Look Up STD

    This table will store the sexual transmitted diseases
    that ModoBio works with
    """

    std_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique ID number identifying the results.

    :type: int, primary key, autoincrement
    """

    std = db.Column(db.String)
    """
    Sexual Transmitted Disease

    :type: str
    """

class MedicalSTDHistory(BaseModelWithIdx, UserIdFkeyMixin):
    """ Medical STD History

    This table stores the client's STD history
    """

    std_id = db.Column(db.Integer, db.ForeignKey('MedicalLookUpSTD.std_id',ondelete="CASCADE"), nullable=False)
    """
    Disease ID

    :type: int, foreign key to :attr: MedicalLookUpSTD.std_id
    """

class MedicalSocialHistory(BaseModelWithIdx, UserIdFkeyMixin):
    """ Medical Social History

    This table is used for client onboarding. It is used for 
    storing the client's medical social information.
    """    

    displayname = 'Medical General Info - Social History'

    ever_smoked = db.Column(db.Boolean)
    """
    Has the client ever smoked

    :type: bool
    """   

    currently_smoke = db.Column(db.Boolean)
    """
    Does the client currently smoke

    :type: bool
    """

    last_smoke_date = db.Column(db.Date)
    """
    Date when client last smoked.

    :type: :class:`datetime.date`
    """    

    last_smoke = db.Column(db.Integer)
    """
    The last time the client smoked

    :type: int
    """

    last_smoke_time = db.Column(db.String)
    """
    Drop down, time frame

    options are months, years
    :type: str
    """

    avg_num_cigs = db.Column(db.Integer)
    """
    Average number of cigarettes smoked per day
    :type: int
    """

    num_years_smoked = db.Column(db.Integer)
    """
    Number of years you have smoked

    :type: int
    """

    plan_to_stop = db.Column(db.Boolean)
    """
    If client is planning to quit smoking

    :type: int
    """

    avg_weekly_drinks = db.Column(db.Integer)
    """
    Average number of drinks client drinks per week

    :type: int
    """
    
    avg_weekly_workouts = db.Column(db.Integer)
    """
    Average number of times client worksout a week

    :type: int
    """

    job_title = db.Column(db.String(100))
    """
    If the client is employed, what is their job title

    :type: str
    """

    avg_hourly_meditation = db.Column(db.Integer)
    """
    Average number of hours client prays/meditates

    :type: int
    """

    sexual_preference = db.Column(db.String)
    """
    Sexual preference men, women, both, prefer not to say

    :type: str
    """

class MedicalFamilyHistory(BaseModelWithIdx, UserIdFkeyMixin):
    """ Personal and Family Medical History

    This table is used for client onboarding. It is used for 
    storing the client's general medical information.
    """    

    displayname = 'Medical General Info - Family History'

    medical_condition_id = db.Column(db.Integer, db.ForeignKey('MedicalConditions.medical_condition_id',ondelete="CASCADE"), nullable=False)
    """
    Disease ID

    :type: int, foreign key to :attr: MedicalConditions.medical_condition_id
    """

    myself = db.Column(db.Boolean)
    """
    If the user has a disease

    :type: bool
    """

    father = db.Column(db.Boolean)
    """
    If the user's father has a disease

    :type: bool
    """

    mother = db.Column(db.Boolean)
    """
    If the user's mother has a disease

    :type: bool
    """

    sister = db.Column(db.Boolean)
    """
    If the user's sister has a disease

    :type: bool
    """

    brother = db.Column(db.Boolean)
    """
    If the user's brother has a disease

    :type: bool
    """

class MedicalConditions(BaseModel):
    """ Medical Conditions Table

    This table will store the medical conditions
    """

    medical_condition_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique ID number identifying the results.

    :type: int, primary key, autoincrement
    """

    category = db.Column(db.String)
    """
    Category for the medical condition.

    **Example**

    * Autoimmune
    * Cancer
    * Cardiovascular

    :type: str
    """

    subcategory = db.Column(db.String)
    """
    Sub category for medical conditions

    **Example**

    * Cardiovascular

        * Bleeding disorder
        * Anemia
        * Chest pain

    :type: str
    """

    condition = db.Column(db.String)
    """
    The medical condition.

    **Example**

    * Cardiovascular

            * Heart murmur

        * Anemia

            * Sickle cell

    :type: str
    """

class MedicalGeneralInfoMedicationAllergy(BaseModelWithIdx, UserIdFkeyMixin):
    """ General Medical Information.

    This table is used for client onboarding. It is used for 
    storing the client's general medical information.
    """    
    displayname = 'Medical General Info - Medication Allergies'

    medication_name = db.Column(db.String)
    """
    Medication name if client has allergic reaction to it

    :type: str
    """

    allergy_symptoms = db.Column(db.String)
    """
    Symptoms of allergies to medication

    :type: str
    """

class MedicalGeneralInfoMedications(BaseModelWithIdx, UserIdFkeyMixin, ReporterIdFkeyMixin):
    """ General Medical Information.

    This table is used for client onboarding. It is used for 
    storing the client's general medical information.
    """    
    displayname = 'Medical General Info - Medications'

    medication_name = db.Column(db.Text)
    """
    Client's Medication/Supplements

    :type: text
    """

    medication_dosage = db.Column(db.Float)
    """
    Client's medication dosage

    :type: float
    """

    medication_units = db.Column(db.String)
    """
    Client's medication units
    mL, mg, g

    :type: str
    """

    medication_freq = db.Column(db.Integer)
    """
    Client's medication frequency
    0-9 times

    medication_freq time(s) per medication_timesper_freq medication_time_units

    :type: int
    """

    medication_times_per_freq = db.Column(db.Integer)
    """
    Client's medication frequency PER unit (hour, day, week)
    0-9 timesper
    medication_freq time(s) per medication_timesper_freq medication_time_units

    :type: int
    """

    medication_time_units = db.Column(db.String)
    """
    Client's medication time units
    (Hour, Day, Week)
    medication_freq time(s) per medication_timesper_freq medication_time_units    

    **Example**

    1 time(s) per 1 Day
    2 time(s) per 1 Week

    :type: str
    """


class MedicalGeneralInfo(BaseModelWithIdx, UserIdFkeyMixin):
    """ General Medical Information.

    This table is used for client onboarding. It is used for 
    storing the client's general medical information.
    """    
    displayname = displayname = 'Medical General Info'

    primary_doctor_contact_name = db.Column(db.String(50))
    """
    Client's primary doctor name

    :type: str, max length 50
    """

    primary_doctor_contact_phone = db.Column(db.String(20))
    """
    Client's primary doctor phone
    
    :type: str, max length 20
    """

    primary_doctor_contact_email = db.Column(db.String, nullable=True)
    """
    Client's primary doctor email
    
    :type: str
    """

    blood_type = db.Column(db.String)
    """
    Client's blood type:
    A, B, AB, O

    :type: str
    """
    
    blood_type_positive = db.Column(db.Boolean)
    """
    Client's blood type sign:
    positive or negative

    :type: bool
    """

class MedicalImaging(BaseModelWithIdx, UserIdFkeyMixin, ReporterIdFkeyMixin):
    """ Medical Imaging table.

    This table stores the medical imaging history of a client. 
    As long as the user_id exists, we can add images to this table and search by user_id
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

class MedicalHistory(BaseModelWithIdx, UserIdFkeyMixin):
    """ Medical history table.
        Deprecated 7.26.21

        MedicalGeneralInfo, MedicalGeneralInfoMedications used instead

        Medical history table.

    This table stores the medical history of a client. The information is taken
    only once, during the initial consult.
    """
    displayname = 'Medical history'

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


class MedicalPhysicalExam(BaseModelWithIdx, UserIdFkeyMixin, ReporterIdFkeyMixin):
    """ Medical physical exam table.

    This table stores the results of the physical exam of a client. The
    information is taken only once, during the initial consult.
    """
    displayname = 'Medical physical examination'

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


class MedicalBloodTests(BaseModel, UserIdFkeyMixin, ReporterIdFkeyMixin):
    """ Blood test table.

    This table stores metadata for blood tests.
    """

    test_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique ID number identifying the test.

    :type: int, primary key, autoincrement
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


class MedicalBloodTestResultTypes(BaseModel):
    """ Blood test evaluation limits.

    Blood test values can be evaluated as lying in "normal" or "optimal"
    ranges. What constitutes as a normal or optimal range depends on gender
    and possibly other factors. The range limits are calculated for each
    client and stored in this table.
    """

    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique ID number identifying the results.

    :type: int, primary key, autoincrement
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


class MedicalBloodTestResults(BaseModelWithIdx):
    """ Blood test result data.

    This table holds the value of a single blood test and the
    evaluation of that value given the normal and optimal ranges
    stored in :class:`MedicalBloodTestResultTypes`.
    """

    test_id = db.Column(db.Integer, db.ForeignKey('MedicalBloodTests.test_id', ondelete="CASCADE"), nullable=False)
    """
    Unique test ID number.

    :type: int, foreign key to :attr:`MedicalBloodTests.testid`
    """

    result_id = db.Column(db.Integer, db.ForeignKey('MedicalBloodTestResultTypes.result_id', ondelete="CASCADE"), nullable=False)
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
    connection.execute(text(BLOODTEST_EVAL.format(target.idx, target.result_id, target.result_value)))

class MedicalSurgeries(BaseModel, UserIdFkeyMixin, ReporterIdFkeyMixin):
    """ 
    History of client surgeries.
    """

    surgery_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique id of the surgery

    :type: int, primary key, autoincrementing
    """

    surgery_category = db.Column(db.String, nullable=False)
    """
    Category of this surgery, must be defined in Constant.py MEDICAL_CONDITIONS['Surgery']

    :type: string
    """

    date = db.Column(db.Date, nullable=False)
    """
    Date of this surgery

    :type: date
    """

    surgeon = db.Column(db.String)
    """
    Name of the surgeon who performed this surgery

    :type: string
    """

    institution = db.Column(db.String)
    """
    Name of the institution where this surgery took place

    :type: string
    """

    notes = db.Column(db.String)
    """
    Notes about this surgery from the reporting staff member

    :type: string
    """

class MedicalExternalMR(BaseModelWithIdx, UserIdFkeyMixin):
    """ 
    External medical records table.

    This table stores medical record ID numbers from external medical institutes. 
    """

    __table_args__ = (
        db.UniqueConstraint('user_id', 'med_record_id', 'institute_id'),)

    med_record_id = db.Column(db.String, nullable=False)
    """
    Medical record id.

    This medical record ID comes from an external medical institution.

    :type: str, non-null, unique
    """

    institute_id = db.Column(db.Integer, db.ForeignKey('MedicalInstitutions.institute_id', ondelete="CASCADE"), nullable=False)
    """
    Medical institute id.

    :type: int, foreign key to :attr:`MedicalInstitutions.institute_id`
    """