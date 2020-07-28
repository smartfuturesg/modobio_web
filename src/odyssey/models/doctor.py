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

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='MedicalHistory_clientid_fkey',ondelete="CASCADE"), nullable=False)
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

    def to_dict(self):
        """retuns all data in ClientSubscriptionContract Model as a dictionary"""
        data = {
            'clientid': self.clientid,
            'last_examination_date': self.last_examination_date,
            'last_examination_reason': self.last_examination_reason,
            'goals': self.goals,
            'concerns': self.concerns,
            'family_history': self.family_history,
            'social_history': self.social_history,
            'allergies': self.allergies,
            'medication': self.medication,
            'diagnostic_xray': self.diagnostic_xray,
            'diagnostic_ctscan': self.diagnostic_ctscan,
            'diagnostic_endoscopy': self.diagnostic_endoscopy,
            'diagnostic_mri': self.diagnostic_mri,
            'diagnostic_ultrasound': self.diagnostic_ultrasound,
            'diagnostic_other': self.diagnostic_other
        }
        return data


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

    def to_dict(self):
        """retuns all data in ClientSubscriptionContract Model as a dictionary"""
        data = {
            'clientid': self.clientid,
            'vital_heartrate': self.vital_heartrate,
            'vital_respiratoryrate': self.vital_respiratoryrate,
            'vital_systolic': self.vital_systolic,
            'vital_diastolic': self.vital_diastolic,
            'vital_temperature': self.vital_temperature,
            'vital_weight': self.vital_weight,
            'vital_height': self.vital_height,
            'cardiac_rrr': self.cardiac_rrr,
            'cardiac_s1s2': self.cardiac_s1s2,
            'cardiac_murmurs': self.cardiac_murmurs,
            'cardiac_murmurs_info': self.cardiac_murmurs_info,
            'cardiac_rubs': self.cardiac_rubs,
            'cardiac_gallops': self.cardiac_gallops,
            'pulmonary_clear': self.pulmonary_clear,
            'pulmonary_wheezing': self.pulmonary_wheezing,
            'pulmonary_wheezing_info': self.pulmonary_wheezing_info,
            'pulmonary_rales': self.pulmonary_rales,
            'pulmonary_rhonchi': self.pulmonary_rhonchi,
            'abdominal_soft': self.abdominal_soft,
            'abdominal_hard': self.abdominal_hard,
            'abdominal_bowel': self.abdominal_bowel,
            'abdominal_hsm': self.abdominal_hsm,
            'abdominal_hsm_info': self.abdominal_hsm_info,
            'notes': self.notes
        }
        return data
