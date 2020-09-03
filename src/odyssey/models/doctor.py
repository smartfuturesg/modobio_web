"""
Database tables for the doctor's portion of the Modo Bio Staff application.
All tables in this module are prefixed with 'Medical'.
"""
from datetime import datetime
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
    Heart rate
    
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
    "Regular rate and rythm" heart sound

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

class MedicalBloodChemistryThyroid(db.Model):
    """ Blood Test - Thyroid results

    This table stores the blood test - thyroid results of clients.
    """
    __tablename__ = 'BloodChemistryThyroid'

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

    def get_attributes(self):
        return ['t3_serum_total','tsi','examination_date','thyroglobulin','t3_resin_uptake','thyroxine_binding_globulin',
            't3_serum_free','t3_serum_reverse','thyroidial_iodine_uptake','t4_serum_free','idx','tsh','thyroxine_index',
            'clientid','t4_serum_total']

    def from_dict(self, data):
        """to be used when a new user is created or a user id edited"""
        attributes = self.get_attributes()
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])
        if isinstance(self.exam_date ,str):
            self.exam_date = datetime.strptime(self.exam_date, '%Y-%m-%d')