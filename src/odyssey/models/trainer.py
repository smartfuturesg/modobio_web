from datetime import datetime

from odyssey import db


class PowerAssessment(db.Model):
    """ Power assessment table
    """

    __tablename__ = 'power_assessment'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """
    
    timestamp = db.Column(db.DateTime)
    """
    Timestamp of the assessment.

    :type: datetime.datetime
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    keiser_upper_r_weight = db.Column(db.Integer)
    """
    keiser push/pull weight (right)

    :type: int
    """

    keiser_upper_r_attempt_1 = db.Column(db.Integer)
    """
    keiser push/pull weight (right) attempt 1 of 3

    :type: int
    """
    
    keiser_upper_r_attempt_2 = db.Column(db.Integer)
    """
    keiser push/pull weight (right) attempt 2 of 3

    :type: int
    """

    keiser_upper_r_attempt_3 = db.Column(db.Integer)
    """
    keiser push/pull weight (right) attempt 3 of 3

    :type: int
    """

    keiser_upper_l_weight = db.Column(db.Integer)
    """
    keiser push/pull weight (left)

    :type: int
    """

    keiser_upper_l_attempt_1 = db.Column(db.Integer)
    """
    keiser push/pull weight (left) attempt 1 of 3

    :type: int
    """

    keiser_upper_l_attempt_2 = db.Column(db.Integer)
    """
    keiser push/pull weight (left) attempt 2 of 3

    :type: int
    """

    keiser_upper_l_attempt_3 = db.Column(db.Integer)
    """
    keiser push/pull weight (left) attempt 3 of 3

    :type: int
    """
    
    keiser_lower_bi_weight = db.Column(db.Integer)
    """
    keiser leg press weight (bilateral)

    :type: int
    """

    keiser_lower_bi_attempt_1 = db.Column(db.Integer)
    """
    keiser leg press attemp 1 of 3 (bilateral)

    :type: int
    """


    keiser_lower_bi_attempt_2 = db.Column(db.Integer)
    """
    keiser leg press attemp 2 of 3 (bilateral)

    :type: int
    """


    keiser_lower_bi_attempt_3 = db.Column(db.Integer)
    """
    keiser leg press attemp 3 of 3 (bilateral)

    :type: int
    """
        
    keiser_lower_r_weight = db.Column(db.Integer)
    """
    keiser leg press weight (right)

    :type: int
    """

    keiser_lower_r_attempt_1 = db.Column(db.Integer)
    """
    keiser leg press attempt 1 of 3 (right)

    :type: int
    """

    keiser_lower_r_attempt_2 = db.Column(db.Integer)
    """
    keiser leg press attempt 2 of 3 (right)

    :type: int
    """

    keiser_lower_r_attempt_3 = db.Column(db.Integer)
    """
    keiser leg press attempt 3 of 3 (right)

    :type: int
    """
        
    keiser_lower_l_weight = db.Column(db.Integer)
    """
    keiser leg press weight (left)

    :type: int
    """

    keiser_lower_l_attempt_1 = db.Column(db.Integer)
    """
    keiser leg press attempt 1 of 3  (left)

    :type: int
    """

    keiser_lower_l_attempt_2 = db.Column(db.Integer)
    """
    keiser leg press attempt 2 of 3  (left)

    :type: int
    """

    keiser_lower_l_attempt_3 = db.Column(db.Integer)
    """
    keiser leg press attempt 3 of 3  (left)

    :type: int
    """

    upper_watts_per_kg = db.Column(db.Float)
    """
    measure of upper body watts per kg

    :type: float
    """

    lower_watts_per_kg = db.Column(db.Float)
    """
    measure of lower body watts per kg
    
    :type: float
    """


class StrengthAssessment(db.Model):
    """ Strength assessment table
    """

    __tablename__ = 'strength_assessment'
    
    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """
    
    timestamp = db.Column(db.DateTime)
    """
    Timestamp of the assessment.

    :type: datetime.datetime
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    upper_push_notes = db.Column(db.Text)
    """
    notes on the push exercise

    :type: str
    """

    upper_pull_notes = db.Column(db.Text)
    """
    notes on the pull exercise

    :type: str
    """

    upper_push_l_weight = db.Column(db.Integer)
    """
    push weight (left)

    :type: int
    """

    upper_push_l_attempt_1 = db.Column(db.Integer)
    """
    push weight (left) attempt 1 of 3

    :type: int
    """
    
    upper_push_l_attempt_2 = db.Column(db.Integer)
    """
    push weight (left) attempt 2 of 3

    :type: int
    """

    upper_push_l_attempt_3 = db.Column(db.Integer)
    """
    push weight (left) attempt 3 of 3

    :type: int
    """

    upper_push_l_estimated_10rm = db.Column(db.Float)
    """
    estimate of 10RM
    
    :type: float
    """

    upper_push_r_weight = db.Column(db.Integer)
    """
    push weight (right)

    :type: int
    """

    upper_push_r_attempt_1 = db.Column(db.Integer)
    """
    push weight (right) attempt 1 of 3

    :type: int
    """
    
    upper_push_r_attempt_2 = db.Column(db.Integer)
    """
    push weight (right) attempt 2 of 3

    :type: int
    """

    upper_push_r_attempt_3 = db.Column(db.Integer)
    """
    push weight (right) attempt 3 of 3

    :type: int
    """

    upper_push_r_estimated_10rm = db.Column(db.Float)
    """
    estimate of 10RM
    
    :type: float
    """

    upper_push_bi_weight = db.Column(db.Integer)
    """
    push weight (bilateral)

    :type: int
    """

    upper_push_bi_attempt_1 = db.Column(db.Integer)
    """
    push weight (bilateral) attempt 1 of 3

    :type: int
    """
    
    upper_push_bi_attempt_2 = db.Column(db.Integer)
    """
    push weight (bilateral) attempt 2 of 3

    :type: int
    """

    upper_push_bi_attempt_3 = db.Column(db.Integer)
    """
    push weight (bilateral) attempt 3 of 3

    :type: int
    """

    upper_push_bi_estimated_10rm = db.Column(db.Float)
    """
    estimate of 10RM
    
    :type: float
    """

    upper_pull_l_weight = db.Column(db.Integer)
    """
    pull weight (left)

    :type: int
    """

    upper_pull_l_attempt_1 = db.Column(db.Integer)
    """
    pull weight (left) attempt 1 of 3

    :type: int
    """
    
    upper_pull_l_attempt_2 = db.Column(db.Integer)
    """
    pull weight (left) attempt 2 of 3

    :type: int
    """

    upper_pull_l_attempt_3 = db.Column(db.Integer)
    """
    pull weight (left) attempt 3 of 3

    :type: int
    """

    upper_pull_l_estimated_10rm = db.Column(db.Float)
    """
    estimate of 10RM
    
    :type: float
    """

    upper_pull_r_weight = db.Column(db.Integer)
    """
    pull weight (right)

    :type: int
    """

    upper_pull_r_attempt_1 = db.Column(db.Integer)
    """
    pull weight (right) attempt 1 of 3

    :type: int
    """
    
    upper_pull_r_attempt_2 = db.Column(db.Integer)
    """
    pull weight (right) attempt 2 of 3

    :type: int
    """

    upper_pull_r_attempt_3 = db.Column(db.Integer)
    """
    pull weight (right) attempt 3 of 3

    :type: int
    """

    upper_pull_r_estimated_10rm = db.Column(db.Float)
    """
    estimate of 10RM
    
    :type: float
    """

    upper_pull_bi_weight = db.Column(db.Integer)
    """
    pull weight (bilateral)

    :type: int
    """

    upper_pull_bi_attempt_1 = db.Column(db.Integer)
    """
    pull weight (bilateral) attempt 1 of 3

    :type: int
    """
    
    upper_pull_bi_attempt_2 = db.Column(db.Integer)
    """
    pull weight (bilateral) attempt 2 of 3

    :type: int
    """

    upper_pull_bi_attempt_3 = db.Column(db.Integer)
    """
    pull weight (bilateral) attempt 3 of 3

    :type: int
    """

    upper_pull_bi_estimated_10rm = db.Column(db.Float)
    """
    estimate of 10RM
    
    :type: float
    """




class MovementAssessment(db.Model):
    """ Movement Assessment table
    """

    __tablename__ = 'movement_assessment'
    
    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """
    
    timestamp = db.Column(db.DateTime)
    """
    Timestamp of the assessment.

    :type: datetime.datetime
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """


class HeartAssessment(db.Model):
    """ Heart assessment table
    """

    __tablename__ = 'heart_assessment'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """
    
    timestamp = db.Column(db.DateTime)
    """
    Timestamp of the assessment.

    :type: datetime.datetime
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """


class MoxyAssessment(db.Model):
    """ Moxy assessment table

    """

    __tablename__ = 'moxy_assessment'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """
    
    timestamp = db.Column(db.DateTime)
    """
    Timestamp of the assessment.

    :type: datetime.datetime
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

class MoxyRipTest(db.Model):
    """ Moxy rop test table
    """

    __tablename__ = 'moxy_rip_test'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """
    
    timestamp = db.Column(db.DateTime)
    """
    Timestamp of the assessment.

    :type: datetime.datetime
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """


class LungAssessment(db.Model):
    """ Lung assessment
    """

    __tablename__ = 'lung_assessment'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """
    
    timestamp = db.Column(db.DateTime)
    """
    Timestamp of the assessment.

    :type: datetime.datetime
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """
