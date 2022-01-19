"""
Database tables for supporting lookup tables. These tables should be static tables only used for reference,
not to be edited at runtime. 
"""
import logging
logger = logging.getLogger(__name__)

from sqlalchemy.orm import relationship
from flask import current_app

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME, ORG_TOKEN_LIFETIME
from odyssey.utils.base.models import BaseModelWithIdx, BaseModel
from odyssey.api.practitioner.models import PractitionerOrganizationAffiliation

class LookupNotificationSeverity(BaseModelWithIdx):
    """
        Lookup table containing notification severity
    """
    severity = db.Column(db.String)
    """
    Severity level

    :type: str
    """

    color = db.Column(db.String)
    """
    hex color

    :type: str
    """

class LookupTermsAndConditions(BaseModelWithIdx):
    """ 
        Holds the documententation for the terms and conditions
    """
    
    terms_and_conditions = db.Column(db.String)
    """ 
    Terms and Conditions

    :type: str
    """    

class LookupBookingTimeIncrements(BaseModelWithIdx):
    """ 
    Holds all time increment from 00:00 to 23:55 in increments of 5 minutes
    """
    
    start_time = db.Column(db.Time)
    """ 
    start time

    :type: datetime.time
    """
    
    end_time = db.Column(db.Time)
    """ 
    end time 

    :type: datetime.time
    """

class LookupProfessionalAppointmentConfirmationWindow(BaseModelWithIdx):
    """ Stored appointment confirmation windows for professionals in database. 
    """

    confirmation_window = db.Column(db.Float)
    """
    confirmation windows for 
    from 1 hour to 24 hours in 30 minute increments
    
    :type: float
    """    

class LookupTransactionTypes(BaseModelWithIdx):
    """ Stored transaction types in database. 
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

class LookupCountriesOfOperations(BaseModelWithIdx):
    """ Stored countries of operations in database. 
    """

    country = db.Column(db.String)
    """
    countries of operations
    
    :type: str
    """
    
class LookupTerritoriesOfOperations(BaseModelWithIdx):
    """ 
    Territories of operaion are organized by country and then sub-territory,
    where a sub_territory is the highest level of governing region that can have
    laws which will impact our business practices. 

    In the United States, the sub_territory will be at the state level.

    Staff members are required to specify which territories they can operate in. 
    """

    country_id = db.Column(db.Integer, db.ForeignKey('LookupCountriesOfOperations.idx'))
    """
    Country in which this territory resides
    
    :type: int, foreign key(LookupCountriesOfOperations.idx)
    """

    sub_territory = db.Column(db.String)
    """
    Sub-territory depends on the country. In the US, this translate to state. 
    
    :type: str
    """

    sub_territory_abbreviation = db.Column(db.String)
    """
    Abbreviation of sub_territory. Two characters for US states.
    
    :type: str
    """

    active = db.Column(db.Boolean)
    """
    True if the territory is operational on the modobio platform

    :type: bool
    """

class LookupClientBookingWindow(BaseModelWithIdx):
    """ Stored booking windows for the client in database. 
    """

    booking_window = db.Column(db.Integer)
    """
    Booking Window
    from 8 hours to 24 hours in increments of 1 hour
    
    :type: int
    """

class LookupTelehealthSessionDuration(BaseModelWithIdx):
    """ Stored telehealth session durations in database. 
    """

    session_duration = db.Column(db.Integer)
    """
    session duration
    from 10 minutes to 60 minutes in increments of 5 minutes
    
    :type: int
    """

class LookupActivityTrackers(BaseModelWithIdx):
    """ Look up table for activity trackers and their capabilities. """

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

class LookupDrinks(BaseModel):
    """ Static list of drinks that a client can purchase or be recommended. 
    """

    drink_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Id of this drink.

    :type: integer, primary key, autoincrementing
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

class LookupDrinkIngredients(BaseModelWithIdx):
    """ List of ingredients that a drink is made up of. 
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

class LookupGoals(BaseModel):
    """ Static list of goals that a client can choose from. 
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

class LookupMacroGoals(BaseModel):
    """ Static list of pre-defined primary health goals available to a client 
    """

    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Id of goal.

    :type: integer, primary key, autoincrementing
    """

    goal = db.Column(db.String)
    """
    Name of goal.

    :type: string
    """

class LookupRaces(BaseModel):
    """ Static list of races that a client can choose from. 
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

class LookupSubscriptions(BaseModel):
    """ Static list of subscription plans that a user can choose from. 
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

class LookupNotifications(BaseModel):
    """ Static list of notifications types that a user can receive. """

    notification_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Id of this notification type.

    :type: int, primary key, autoincrementing
    """

    notification_type = db.Column(db.String(50))
    """
    Name of this notification type.

    :type: str, max length 50
    """

    icon = db.Column(db.String(50))
    """
    Icon used for this notification type, denotes a file in an s3 bucket.

    :type: str, max length 50
    """

    background_color = db.Column(db.String(50))
    """
    Background color used for this notification type.
    Color names are from the list of 140 colors supported by all browsers.
    See: https://htmlcolorcodes.com/color-names/

    :type: str, max length 50
    """

    symbol_color = db.Column(db.String(50))
    """
    Symbol color used for this notification type.
    Color names are from the list of 140 colors supported by all browsers.
    `original` means do not apply any color to the svg.
    See: https://htmlcolorcodes.com/color-names/

    :type: str, max length 50
    """


class LookupClinicalCareTeamResources(BaseModel):
    """
    Stores all the database tables which can be accessed by a clinical care team.
    Table names are given an index in order to be referenced by other tables
    """

    resource_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    ID for the table. 

    :type: integer, primary key, autoincrementing
    """

    resource_name = db.Column(db.String)
    """
    Table name 

    :type: string
    """

    display_name = db.Column(db.String)
    """
    Name of resource to display to client. We do not want table names getting passed around.
    
    :type: string
    """

    resource_group = db.Column(db.String)
    """
    Some resources can be grouped together for display. Otherwise this will be None
    
    :type: string
    """

    access_group = db.Column(db.String)
    """
    Grouping as it relates to practitioner and staff roles. Current access groups are 'general' (for generic client info which all practitioners 
    should have access to) and 'medical_doctor' (resources specific to the medical_doctor role).

    :type: string
    """

class LookupDefaultHealthMetrics(BaseModelWithIdx):
    """
    Health metric recommendations by sex and age category
    Most of this data may be obtained from one more more fitness trackers

    The intended use of this table is to show clients the types of goals and associated benchmarks
    they shoudld strive for. We may also venture to use the data in this table to evaluate where 
    clients stand among these metrics.  
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

class LookupEmergencyNumbers(BaseModelWithIdx):
    """ Static list of emergency contact phone numbers """

    continent = db.Column(db.String)
    """
    Continent for the emergency phone number

    :type: string
    """

    country = db.Column(db.String)
    """
    Country for the emergency phone number

    :type: string
    """

    code = db.Column(db.String, primary_key=True)
    """
    Country ISO aplha-2 code, a two letter code for the country

    :type: string
    """

    service = db.Column(db.String)
    """
    Service name for the emergency phone number (Ambulance, Police or Fire)

    :type: string
    """

    phone_number = db.Column(db.String)
    """
    Emergency phone number

    :type: string
    """

class LookupRoles(BaseModelWithIdx):

    role_name = db.Column(db.String, unique=True)
    """
    Internal name of this role that is used throughout the code.

    :type: string
    """

    professionals_assigned = db.relationship('StaffRoles', uselist=True, back_populates='role_info')
    """
    One to many relationship with staff roles table
    :type: :class:`StaffRoles` instance list
    """

    display_name = db.Column(db.String)
    """
    Display name of this role that should be presented in user-facing applications.

    :type: string
    """

    alt_role_name = db.Column(db.String)
    """
    List of alternate user-facing names that may be utilized in the future.

    :type: string
    """

    is_practitioner = db.Column(db.Boolean)
    """
    Denotes if this role is a practioner or not.

    :type: boolean
    """

    color = db.Column(db.String)
    """
    Hex color code that denotes what color should be used to color certain UI assets for this role

    :type: string
    """

    icon = db.Column(db.String)
    """
    Icon that should be used for this profession type

    :type: string
    """

    has_client_data_access = db.Column(db.Boolean)
    """
    Denotes if this role has access to client data

    :type: boolean
    """

    active = db.Column(db.Boolean)
    """
    Denotes whether a role type is currently used in the system.
    Roles will be activated in further versions when needed.

    :type: boolean
    """

    notes = db.Column(db.String)
    """
    Notes about this role.

    :type: string
    """

class LookupLegalDocs(BaseModelWithIdx):

    name = db.Column(db.String)
    """
    Name of this document.

    :type: string
    """

    version = db.Column(db.Integer)
    """
    Version # of this document.

    :type: int
    """

    target = db.Column(db.String)
    """
    Target of this document. Types are 'User', 'Professional', and 'Practitioner'.

    :type: string
    """

    path = db.Column(db.String)
    """
    Path to this document.

    :type: string
    """

class LookupMedicalSymptoms(BaseModelWithIdx):
    """
    Lookup table for medical symptoms and their ICD-10 codes.
    """

    name = db.Column(db.String)
    """
    Name of this symptom.

    :type: string
    """

    code = db.Column(db.String)
    """
    ICD-10 code for this symptom.

    :type: string
    """
class LookupOrganizations(BaseModelWithIdx):
    """
    Lookup table for organizations affiliated with Modobio.
    """

    org_name = db.Column(db.String)
    """
    Name of this organization.

    :type: string
    """

    org_id = db.Column(db.String)
    """
    Unique randomly generated ID for this organization.

    :type: string
    """

    org_token = db.Column(db.String)
    """
    Token used by this organization for access. Expires after 6 months.

    :type: string
    """

    practitioners_assigned = db.relationship('PractitionerOrganizationAffiliation', uselist=True, back_populates='org_info')
    """
    One to many relationship with pracitioner organization affiliation table
    :type: :class:`PractitionerOrganizationAffiliation` instance list
    """

class LookupCurrencies(BaseModelWithIdx):
    """
    Lookup table for accepted currency types.

    9/30/2021 - Added the notion of minimum and maximum rate
                the practitioner will charge their client
    """

    country = db.Column(db.String, nullable=False)
    """
    The country associated with this cost. Must be present in at least one entry in LookupTerritoriesOfOperation.country

    :type: string
    """

    symbol_and_code = db.Column(db.String, nullable=False)
    """
    symbol (ex. $, €) and code (ex. USD, EUR)

    :type: string
    """

    min_rate = db.Column(db.Numeric(10,2, asdecimal=False))
    """
    Minimum HOURLY rate the practitioner can charge
    
    :type: Numeric
    """

    max_rate = db.Column(db.Numeric(10,2, asdecimal=False))
    """
    Maximum HOURLY rate the practitioner can charge
    
    :type: Numeric
    """
    
    increment = db.Column(db.Integer)
    """
    Increment from min_rate up to max_rate

    :type: int
    """    

class LookupBloodTests(BaseModel):
    """
    Lookup table for blood tests
    """
    
    modobio_test_code = db.Column(db.String, primary_key=True, nullable=False)
    """
    Internal test code
    
    :type: string, primary key
    """
    
    display_name = db.Column(db.String)
    """
    Test display name
    
    :type: string
    """
    
    quest_test_code = db.Column(db.String)
    """
    Quest Diagnostics test code
    
    :type: string
    """
    
    cpt_test_code = db.Column(db.String)
    """
    Current Procedural Terminology (medical billing) code
    
    :type: string
    """
    
    panel_display_name = db.Column(db.String)
    """
    Name of the blood panel where the test results come from
    
    :type: string
    """
    
    tags = db.Column(db.String)
    """
    Tags relating the this test
    
    :type: string
    """
    
    ranges = db.Relationship('LookupBloodTestRanges')
    """
    Relation holding information on ranges that apply to this test type.
    
    :type: :class: LookupBloodTestRanges
    """
    
class LookupBloodTestRanges(BaseModelWithIdx):
    """
    Lookup table for blood test result optimal/critical ranges. One result may have multiple
    entries if it can be affected by age/race/fertility status/bioloical sex
    """
    
    modobio_test_code = db.Column(db.String, db.ForeignKey('LookupBloodTests.modobio_test_code'))
    """
    Modobio Test Code for this result.
    
    :type: string, foreign key(LookupBloodTests.modobio_test_code)
    """
    
    test_info = db.Relationship("LookupBloodTests", back_populates="ranges")
    """
    Many to one relationship holding the non-range test information.
    
    :type: :class: LookupBloodTests
    """
    
    biological_sex_male = db.Column(db.Boolean)
    """
    Biological sex this range applies to. If Null, the range applies to either biological sex.
    
    :type: bool
    """
    
    menstrual_cycle = db.Column(db.String)
    """
    Stage of the menstrual cycle this range applies to. If Null, the range applies to any stage.
    
    :type: string
    """
    
    age_min = db.Column(db.Integer)
    """
    Minimum age this range applies to.
    
    :type: int
    """
    
    age_max = db.Column(db.Integer)
    """
    Maximum age this range applies to.
    
    :type: int
    """
    
    race_id = db.Column(db.Integer, db.ForeignKey('LookupRaces.race_id'))
    """
    Race_id this range applies to. If Null, the range applies to all races.
    
    :type: int, foreign key(LookupRaces.race_id)
    """
    
    units = db.Column(db.String)
    """
    Units used to measure this result.
    
    :type: string
    """
    
    ratio = db.Column(db.String)
    """
    Ratio used to calculate this result if applicable
    
    :type: string
    """
    
    critical_min = db.Column(db.Float)
    """
    Critical range minimum.
    
    :type: float    
    """
    
    ref_min = db.Column(db.Float)
    """
    Reference (normal) range minimum
    
    :type: float
    """ 
    
    ref_max = db.Column(db.Float)
    """
    Reference (normal) range maximum
    
    :type: float
    """
    
    critical_max = db.Column(db.Float)
    """
    Critical range maximum.
    
    :type: float
    """