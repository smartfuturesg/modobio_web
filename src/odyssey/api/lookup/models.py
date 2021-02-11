"""
Database tables for supporting lookup tables. These tables should be static tables only used for reference,
not to be edited at runtime. 
"""

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

class LookupClientBookingWindow(db.Model):
    """ Stored booking windows for the client in database. 
    """

    __tablename__ = 'LookupClientBookingWindow'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Primary index for 

    :type: int, primary key, autoincrement
    """

    booking_window = db.Column(db.Integer)
    """
    Booking Window
    from 8 hours to 24 hours in increments of 1 hour
    
    :type: int
    """

class LookupTelehealthSessionCost(db.Model):
    """ Stored telehealth session costs in database. 
    """

    __tablename__ = 'LookupTelehealthSessionCost'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Primary index for 

    :type: int, primary key, autoincrement
    """

    profession_type = db.Column(db.String)
    """
    Profession Type 
    i.e. Medical Doctor etc

    :type: str
    """

    territory = db.Column(db.String)
    """
    Territory
    i.e. USA, UK, etc

    :type: str
    """

    session_cost = db.Column(db.Integer)
    """
    session cost in that country's currency
    
    :type: int
    """

class LookupTelehealthSessionDuration(db.Model):
    """ Stored telehealth session durations in database. 
    """

    __tablename__ = 'LookupTelehealthSessionDuration'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Primary index for 

    :type: int, primary key, autoincrement
    """

    session_duration = db.Column(db.Integer)
    """
    session duration
    from 10 minutes to 60 minutes in increments of 5 minutes
    
    :type: int
    """

class LookupActivityTrackers(db.Model):
    """ Look up table for activity trackers and their capabilities. """

    __tablename__ = 'LookupActivityTrackers'

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

    brand = db.Column(db.String)
    """
    activity tracker brand name

    :type: str
    """

    series = db.Column(db.String)
    """
    activity tracker series

    :type: str
    """

    model = db.Column(db.String)
    """
    activity tracker model

    :type: str
    """

    ecg_metric_1 = db.Column(db.Boolean)
    """
    2-lead ECG Metric 1
    Text

    :type: bool
    """

    ecg_metric_2 = db.Column(db.Boolean)
    """
    2-lead ECG Metric 2
    Beats Per Minute

    :type: bool
    """

    sp_o2_spot_check = db.Column(db.Boolean)
    """
    % Oxygenation (no decimals)

    :type: bool
    """

    sp_o2_nighttime_avg = db.Column(db.Boolean)
    """
    % Oxygenation (no decimals)

    :type: bool
    """

    sleep_total = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    deep_sleep = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    rem_sleep = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    quality_sleep = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    light_sleep = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    awake = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    sleep_latency = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

    bedtime_consistency = db.Column(db.Boolean)
    """
    + or - Time HH:MM

    :type: bool
    """                            

    wake_consistency = db.Column(db.Boolean)
    """
    + or - Time HH:MM

    :type: bool
    """

    rhr_avg = db.Column(db.Boolean)
    """
    beats per minute

    :type: bool
    """    

    rhr_lowest = db.Column(db.Boolean)
    """
    beats per minute

    :type: bool
    """    
    
    hr_walking = db.Column(db.Boolean)
    """
    beats per minute

    :type: bool
    """     

    hr_24hr_avg = db.Column(db.Boolean)
    """
    beats per minute

    :type: bool
    """ 

    hrv_avg = db.Column(db.Boolean)
    """
    milliseconds (ms)

    :type: bool
    """    

    hrv_highest = db.Column(db.Boolean)
    """
    milliseconds (ms)

    :type: bool
    """

    respiratory_rate = db.Column(db.Boolean)
    """
    per minute

    :type: bool
    """

    body_temperature = db.Column(db.Boolean)
    """
    + or - degrees farenheit

    :type: bool
    """

    steps = db.Column(db.Boolean)
    """
    number
    
    :type: bool
    """

    total_calories = db.Column(db.Boolean)
    """
    calories (kcal)

    :type: bool
    """

    active_calories = db.Column(db.Boolean)
    """
    calories

    :type: bool
    """
    
    walking_equivalency = db.Column(db.Boolean)
    """
    number miles

    :type: bool
    """

    inactivity = db.Column(db.Boolean)
    """
    Time HH:MM

    :type: bool
    """

class LookupDrinks(db.Model):
    """ Static list of drinks that a client can purchase or be recommended. 
    """

    __tablename__ = 'LookupDrinks'

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

    drink_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique id for this drink.

    :type: int, primary key, autoincrement
    """

    primary_goal_id = db.Column(db.Integer, db.ForeignKey('LookupGoals.goal_id'), nullable=False)
    """
    Id of the primary goal that is aided by this drink.

    :type: string
    """

    color = db.Column(db.String)
    """
    Color of this drink.

    :type: string
    """

class LookupDrinkIngredients(db.Model):
    """ List of ingredients that a drink is made up of. 
    """

    __tablename__ = 'LookupDrinkIngredients'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    drink_id = db.Column(db.Integer, db.ForeignKey('LookupDrinks.drink_id'), nullable=False)
    """
    Id of the drink this ingredient belongs to.

    :type: int, foreign key(LookupDrinks.drink_id)
    """

    is_primary_ingredient = db.Column(db.Boolean)
    """
    Denotes if this ingredient is they primary ingredient in the drink.

    :type: boolean
    """

    is_key_additive = db.Column(db.Boolean)
    """
    Denotes if this ingredient is a key additive in the drink.

    :type: boolean
    """

    ingredient_name = db.Column(db.String)
    """
    Name of the ingredient.

    :type: string
    """

    amount = db.Column(db.Float)
    """
    Numerical value of the measurement.

    :type: float
    """

    unit = db.Column(db.String)
    """
    Unit of the measurement.

    :type: string
    """

class LookupGoals(db.Model):
    """ Static list of goals that a client can choose from. 
    """

    __tablename__ = 'LookupGoals'

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

    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Id of this goal.

    :type: integer, primary key, autoincrementing
    """

    goal_name = db.Column(db.String)
    """
    Name of this goal.

    :type: string
    """

class LookupRaces(db.Model):
    """ Static list of races that a client can choose from. 
    """

    __tablename__ = 'LookupRaces'

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

    race_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Id of this race.

    :type: integer, primary key, autoincrementing
    """

    race_name = db.Column(db.String)
    """
    Name of this race.

    :type: string
    """

class LookupSubscriptions(db.Model):
    """ Static list of subscription plans that a user can choose from. 
    """

    __tablename__ = 'LookupSubscriptions'

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

    sub_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Id of this subscription plan.

    :type: integer, primary key, autoincrementing
    """

    name = db.Column(db.String)
    """
    Name of this subscription plan.

    :type: string
    """

    description = db.Column(db.String)
    """
    Description of this subscription plan.

    :type: string
    """

    cost = db.Column(db.Float)
    """
    Cost of this subscription plan in USD.

    :type: float
    """

    frequency = db.Column(db.String)
    """
    Frequency that this subscription plan is paid, must be one of (weekly, monthly, annually)

    :type: string
    """

class LookupDefaultHealthMetrics(db.Model):
    """
    Health metric recommendations by sex and age category
    Most of this data may be obtained from one more more fitness trackers

    The intended use of this table is to show clients the types of goals and associated benchmarks
    they shoudld strive for. We may also venture to use the data in this table to evaluate where 
    clients stand among these metrics.  
    """

    __tablename__ = 'LookupDefaultHealthMetrics'

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

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Index

    :type: integer, primary key, autoincrementing
    """

    sex = db.Column(db.String(2))
    """
    Biological sex of the client. Many of the following metrics vary on sex.

    :type: string
    """

    age = db.Column(db.Integer)
    """
    Age category. For adults, the age spacings are 5 years. Most metrics do not vary at these intervals. 

    :type: integer
    """

    bmi_underweight = db.Column(db.Float)
    """
    BMI below which is considered underweight

    :type: float
    """

    bmi_normal_min = db.Column(db.Float)
    """
    Lower point for normal BMI range

    :type: float
    """

    bmi_normal_max = db.Column(db.Float)
    """
    Higher point for normal BMI range

    :type: float
    """

    bmi_overweight_min = db.Column(db.Float)
    """
    Lower point for overweight BMI range

    :type: float
    """

    bmi_overweight_max = db.Column(db.Float)
    """
    Higher point for normal BMI range

    :type: float
    """

    bmi_obese = db.Column(db.Float)
    """
    BMI above which is considered obese

    :type: float
    """

    ecg_metric_1 = db.Column(db.String)
    """
    Metric to look out for from ECG readings

    :type: string
    """

    ecg_metric_2_bpm_min = db.Column(db.Integer)
    """
    BPM reading from ECG analysis. Lower point for healthy BPM range.

    :type: integer
    """

    ecg_metric_2_bpm_max = db.Column(db.Integer)
    """
    BPM reading from ECG analysis. Higher point for healthy BPM range.

    :type: integer
    """

    sp_o2_spot_check = db.Column(db.Integer)
    """
    Minimum healthy SpO2 spot check. 

    :type: integer
    """

    sp_o2_nighttime_avg = db.Column(db.Integer)
    """
    Minimum healthy SpO2 nighttime average. 

    :type: integer
    """

    sleep_total_minutes = db.Column(db.Integer)
    """
    Total minutes of sleep per night recommended

    :type: integer
    """

    sleep_deep_min_minutes = db.Column(db.Integer)
    """
    Total minimum minutes of deep sleep per night recommended

    :type: integer
    """
    
    sleep_deep_max_minutes = db.Column(db.Integer)
    """
    Total maximum minutes of deep sleep per night recommended

    :type: integer
    """

    sleep_rem_min_minutes = db.Column(db.Integer)
    """
    Total minimum minutes of rem sleep per night recommended

    :type: integer
    """

    sleep_rem_max_minutes = db.Column(db.Integer)
    """
    Total maximum minutes of rem sleep per night recommended

    :type: integer
    """

    sleep_quality_min_minutes = db.Column(db.Integer)
    """
    Total minimum minutes of quality sleep per night recommended

    :type: integer
    """

    sleep_quality_max_minutes = db.Column(db.Integer)
    """
    Total maximum minutes of quality sleep per night recommended

    :type: integer
    """

    sleep_light_minutes = db.Column(db.Integer)
    """
    Total minutes of light sleep per night recommended

    :type: integer
    """

    sleep_time_awake_minutes = db.Column(db.Integer)
    """
    Total minutes awake per night of sleep recommended

    :type: integer
    """

    sleep_latency_minutes = db.Column(db.Integer)
    """
    Recommended maximum time to get to sleep once at rest

    :type: integer
    """

    bedtime_consistency_minutes = db.Column(db.Integer)
    """
    Recommended maximum variability in bedtimes 

    :type: integer
    """

    wake_consistency_minutes = db.Column(db.Integer)
    """
    Recommended maximum variability in wake time 
    
    :type: integer
    """

    heart_rate_rest_average_min = db.Column(db.Integer)
    """
    Lower end of recommended average resting heart rate range
    
    :type: integer
    """

    heart_rate_rest_average_max = db.Column(db.Integer)
    """
    Higher end of recommended average resting heart rate range
    
    :type: integer
    """

    heart_rate_rest_lowest_min = db.Column(db.Integer)
    """
    Lower end of recommended resting heart rate range upon spot check
    
    :type: integer
    """

    heart_rate_rest_lowest_max = db.Column(db.Integer)
    """
    Higher end of recommended resting heart rate range upon spot check
    
    :type: integer
    """

    heart_rate_walking_min = db.Column(db.Integer)
    """
    Lower end of recommended walking heart rate range 
    
    :type: integer
    """

    heart_rate_walking_max = db.Column(db.Integer)
    """
    Higher end of recommended walking heart rate range 
    
    :type: integer
    """

    heart_rate_average_min = db.Column(db.Integer)
    """
    Lower end of recommended overall average heart rate range 
    
    :type: integer
    """

    heart_rate_average_max = db.Column(db.Integer)
    """
    Higher end of recommended overall average heart rate range 
    
    :type: integer
    """

    heart_rate_variability_average_milliseconds = db.Column(db.Integer)
    """
    Average recommended heart rate variability (HRV) reported in milliseconds 
    
    :type: integer
    """

    heart_rate_variability_highest_milliseconds = db.Column(db.Integer)
    """
    Higherst recommended heart rate variability (HRV) reported in milliseconds 
    
    :type: integer
    """

    respiratory_rate_min_per_minute = db.Column(db.Integer)
    """
    Minimum respiratory rater (per minute) in recommended range
    
    :type: integer
    """

    respiratory_rate_max_per_minute = db.Column(db.Integer)
    """
    Maximum respiratory rater (per minute) in recommended range
    
    :type: integer
    """

    body_temperature_deviation_fahrenheit = db.Column(db.Float)
    """
    Recommended body temperature variability reported in degrees fahrenheit
    
    :type: float
    """

    steps_per_day = db.Column(db.Integer)
    """
    Steps per day recommended
    
    :type: integer
    """

    steps_walking_equivalency_miles = db.Column(db.Integer)
    """
    Walking distance equivalency of recommended steps perday. Average height of US male and female used for all
    age categories. 
    
    :type: integer
    """
    calories_total = db.Column(db.Integer)
    """
    Total caloreies used by the body over a day. Recommended values are based on the average height and weight 
    of US males and females accross all age categories. 

    :type: integer
    """

    calories_active_burn_min = db.Column(db.Integer)
    """
    Lower end of active calorie burn recommended per day
    
    :type: integer
    """

    calories_active_burn_max = db.Column(db.Integer)
    """
    Higher end of active calorie burn recommended per day
    
    :type: integer
    """

    inactivity_minutes = db.Column(db.Integer)
    """
    Maximum minutes of inactivity recommended per day    

    :type: integer
    """