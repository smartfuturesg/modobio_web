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
