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

    squat_dept = db.Column(db.String)
    """
    Regarding squat depth, the client  ust be one of the following
    'Above Parallel',
    'Parallel',
    'Below Parallel',
    'Full Depth'

    :type: str
    """

    squat_ramp = db.Column(db.String)
    """
    If client requires a ramp to squat, must be one of the following:
    '30 Degree Ramp',
    '15 Degree Ramp',
    'No Ramp'

    :type: str
    """

    squat_eye_test = db.Column(db.Boolean)
    """
    pass-True fail-False of wheather client passes test

    :type: Boolean
    """

    squat_can_breathe = db.Column(db.Boolean)
    """
    while squatting client:
    can breathe-True 
    cannot breathe-False 

    :type: Boolean
    """

    squat_can_look_up = db.Column(db.Boolean)
    """
    while squatting client:
    can look up-True 
    cannot look up-False 

    :type: Boolean
    """

    toe_touch_depth = db.Column(db.String)
    """
    Depth of toe touch test
    'Knee Height',
    'Mid Shin',
    'Low Shin',
    'Toes',
    'Floor'

    :type: str
    """

    toe_touch_pelvis_movement =db.Column(db.String)
    """
    Pelvis movement during toe touch test
    'Right Hip High',
    'Right Hip Back',
    'Left Hip High',
    'Left Hip Back',
    'Even Bilaterally'

    :type: str
    """

    toe_touch_ribcage_movement = db.Column(db.String)
    """
    Ribcage movement during toe touch test
    'Right Posterior Ribcage High',
    'Right Posterior Ribcage Back',
    'Left Posterior Ribcage High',
    'Left Posterior Ribcage Back',
    'Even Bilaterally'

    :type: str
    """

    toe_touch_notes = db.Column(db.String)
    """
    Notes regarding toe touch test

    :type: str
    """ 

    standing_rotation_r_notes = db.Column(db.String)
    """
    Notes regarding standing rotation right

    :type: str
    """ 

    standing_rotation_l_notes = db.Column(db.String)
    """
    Notes regarding standing rotation right

    :type: str
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

    resting_hr = db.Column(db.Integer)
    """
    resting heartrate

    :type: int
    """

    max_hr = db.Column(db.Integer)
    """
    maximum measured heartrate

    :type: int
    """
   
    theoretical_max_hr = db.Column(db.Integer)
    """
    theoretical maximum heartrate

    :type: int
    """ 

    avg_eval_hr = db.Column(db.Integer)
    """
    average heartrate during evaluation

    :type: int
    """

    avg_training_hr = db.Column(db.Integer)
    """
    avergage heatrate during training

    :type: int
    """

    estimated_vo2_max = db.Column(db.Integer)
    """
    estimation of VO2 Max

    :type: int
    """

    notes = db.Column(db.String)
    """
    Notes on the client's heatrate tests

    :type: str
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
    
    notes = db.Column(db.String)
    """
    Notes on the client's moxy tests

    :type: str
    """

    recovery_baseline = db.Column(db.Integer)
    """

    :type: int
    """

    performance_baseline = db.Column(db.Integer)
    """

    :type: int
    """    

    gas_tank_size = db.Column(db.Integer)
    """

    :type: int
    """
    
    starting_sm_o2 = db.Column(db.Integer)
    """

    :type: int
    """

    starting_thb = db.Column(db.Integer)
    """

    :type: int
    """

    limiter = db.Column(db.String)
    """
    Must be one of:
    'Demand',
    'Supply',
    'Respiratory'

    :type: str
    """    

    intervention = db.Column(db.String)
    """
    text box of letters and numbers

    :type: str
    """

    performance_metric_1 = db.Column(db.String)
    """
    Must be one of:
    'Watts',
    'Lbs',
    'Feet/Min'

    :type: str
    """   

    performance_metric_1_value = db.Column(db.Integer)
    """
    The number behind the performance metric 

    :type: int
    """

    performance_metric_2 = db.Column(db.String)
    """
    Must be one of:
    'Watts',
    'Lbs',
    'Feet/Min'

    :type: str
    """   

    performance_metric_2_value = db.Column(db.Integer)
    """
    The number behind the performance metric 
    
    :type: int
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
    
    performance_smo2_1 = db.Column(db.Integer)
    """
    performance assessment 1 smo2

    :type: int
    """

    performance_thb_1 = db.Column(db.Integer)
    """
    performance assessment 1 thb

    :type: int
    """

    performance_average_power_1 = db.Column(db.Integer)
    """
    performance assessment 1 average power

    :type: int
    """

    performance_hr_max_1 = db.Column(db.Integer)
    """
    performance assessment 1 max hr

    :type: int
    """

    performance_smo2_2 = db.Column(db.Integer)
    """
    performance assessment 2 smo2

    :type: int
    """

    performance_thb_2 = db.Column(db.Integer)
    """
    performance assessment 2 thb

    :type: int
    """

    performance_average_power_2 = db.Column(db.Integer)
    """
    performance assessment 2 average power

    :type: int
    """

    performance_hr_max_2 = db.Column(db.Integer)
    """
    performance assessment 2 max hr

    :type: int
    """

    performance_smo2_3 = db.Column(db.Integer)
    """
    performance assessment 3 smo2

    :type: int
    """

    performance_thb_3 = db.Column(db.Integer)
    """
    performance assessment 3 thb

    :type: int
    """

    performance_average_power_3 = db.Column(db.Integer)
    """
    performance assessment 3 average power

    :type: int
    """

    performance_hr_max_3 = db.Column(db.Integer)
    """
    performance assessment 3 max hr

    :type: int
    """
    
    performance_smo2_4 = db.Column(db.Integer)
    """
    performance assessment 4 smo2

    :type: int
    """

    performance_thb_4 = db.Column(db.Integer)
    """
    performance assessment 4 thb

    :type: int
    """

    performance_average_power_4 = db.Column(db.Integer)
    """
    performance assessment 4 average power

    :type: int
    """

    performance_hr_max_4 = db.Column(db.Integer)
    """
    performance assessment 4 max hr

    :type: int
    """

    recovery_smo2_1 = db.Column(db.Integer)
    """
    recovery assessment 1 smo2

    :type: int
    """

    recovery_thb_1 = db.Column(db.Integer)
    """
    recovery assessment 1 thb

    :type: int
    """

    recovery_average_power_1 = db.Column(db.Integer)
    """
    recovery assessment 1 average power

    :type: int
    """

    recovery_hr_min_1 = db.Column(db.Integer)
    """
    recovery assessment 1 min hr

    :type: int
    """

    recovery_smo2_2 = db.Column(db.Integer)
    """
    recovery assessment 2 smo2

    :type: int
    """

    recovery_thb_2 = db.Column(db.Integer)
    """
    recovery assessment 2 thb

    :type: int
    """

    recovery_average_power_2 = db.Column(db.Integer)
    """
    recovery assessment 2 average power

    :type: int
    """

    recovery_hr_min_2 = db.Column(db.Integer)
    """
    recovery assessment 2 min hr

    :type: int
    """

    recovery_smo2_3 = db.Column(db.Integer)
    """
    recovery assessment 3 smo2

    :type: int
    """

    recovery_thb_3 = db.Column(db.Integer)
    """
    recovery assessment 3 thb

    :type: int
    """

    recovery_average_power_3 = db.Column(db.Integer)
    """
    recovery assessment 3 average power

    :type: int
    """

    recovery_hr_min_3 = db.Column(db.Integer)
    """
    recovery assessment 3 min hr

    :type: int
    """
    
    recovery_smo2_4 = db.Column(db.Integer)
    """
    recovery assessment 4 smo2

    :type: int
    """

    recovery_thb_4 = db.Column(db.Integer)
    """
    recovery assessment 4 thb

    :type: int
    """

    recovery_average_power_4 = db.Column(db.Integer)
    """
    recovery assessment 4 average power

    :type: int
    """

    recovery_hr_min_4 = db.Column(db.Integer)
    """
    recovery assessment 4 min hr

    :type: int
    """

    smo2_tank_size = db.Column(db.Integer)
    """
    SmO2 tank size

    :type: int
    """

    thb_tank_size = db.Column(db.Integer)
    """
    tHB tank size

    :type: int
    """

    performance_baseline_smo2 = db.Column(db.Integer)
    """
    performance baseline SmO2 

    :type: int
    """

    performance_baseline_thb = db.Column(db.Integer)
    """
    performance baseline tHB

    :type: int
    """

    recovery_baseline_smo2 = db.Column(db.Integer)
    """
    recovery baseline SmO2 

    :type: int
    """

    recovery_baseline_thb = db.Column(db.Integer)
    """
    recovery baseline tHB

    :type: int
    """

    avg_watt_kg = db.Column(db.Float)
    """
    Average watts per kg

    :type: float
    """

    avg_interval_time = db.Column(db.Integer)
    """
    Average interval time in seconds 

    :type: int
    """

    avg_recovery_time = db.Column(db.Integer)
    """
    Average recovery time in seconds 

    :type: int
    """
    
    limiter = db.Column(db.String)
    """
    Must be one of:
    'Demand',
    'Supply',
    'Respiratory'

    :type: str
    """    

    intervention = db.Column(db.String)
    """
    note. Letters & numbers

    :type: str
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

    notes = db.Column(db.String)
    """
    Notes on the client's lung tests

    :type: str
    """

    bag_size = db.Column(db.Float)
    """
    Lung capcity in liters

    :type: float
    """

    duration = db.Column(db.Integer)
    """
    seconds (0-300)

    :type: int
    """

    breaths_per_minute = db.Column(db.Integer)
    """
    breathing rate

    :type: int
    """

    max_minute_volume = db.Column(db.Float)
    """
    MMV 0-500

    :type: float
    """

    liters_min_kg = db.Column(db.Float)
    """
    liters per minute per kg (0-100)

    :type: float
    """



