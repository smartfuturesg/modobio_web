"""
Database tables for supporting lookup tables. These tables should be static tables only used for reference,
not to be edited at runtime. 
"""

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

class LookupTransactionTypeIcons(db.Model):
""" Stored transaction type icons in database. 
    """

    __tablename__ = 'LookupTransactionTypeIcons'

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

    name = db.Column(db.String)
    """
    Name
    The name of the icon image
    
    :type: str
    """

    icon = db.Column(db.Text)
    """
    icon
    Referenced image name for the FE to use

    :type: text
    """

    mimetype = db.Column(db.Text)


class LookupTransactionTypes(db.Model):
    """ Stored transaction types in database. 
    """

    __tablename__ = 'LookupTransactionTypes'

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

    category = db.Column(db.String)
    """
    Category
    The overall category of the transaction type.
    
    :type: str
    """

    name = db.Column(db.String)
    """
    Name
    The name or subcategory further describing the 
    transaction type if any.
    
    :type: str
    """

    icon = db.Column(db.String)
    """
    icon
    Referenced image name for the FE to use

    :type: str
    """        

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