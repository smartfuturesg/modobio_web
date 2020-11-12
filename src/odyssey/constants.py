""" Various constants used throughout the Odyssey package. """
import enum

from sqlalchemy import text

TABLE_TO_URI = {'ClientPolicies' : '/client/policies/{}/',
                'ClientRelease': '/client/release/{}/',
                'ClientConsent' : '/client/consent/{}/',
                'ClientConsultContract' : '/client/consultcontract/{}/',
                'ClientIndividualContract' : '/client/servicescontract/{}/' ,
                'ClientSubscriptionContract' : '/client/subscriptioncontract/{}/',
                'TrainerFitnessQuestionnaire': '/trainer/questionnaire/{}/',
                'MedicalHistory': '/doctor/medicalhistory/{}/',
                'PTHistory': '/pt/history/{}/',
                'MedicalPhysicalExam': '/doctor/physical/{}/'
                }

COUNTRIES = (
    ('AF', 'Afghanistan'),
    ('AX', 'Åland Islands'),
    ('AL', 'Albania'),
    ('DZ', 'Algeria'),
    ('AS', 'American Samoa'),
    ('AD', 'Andorra'),
    ('AO', 'Angola'),
    ('AI', 'Anguilla'),
    ('AQ', 'Antarctica'),
    ('AG', 'Antigua and Barbuda'),
    ('AR', 'Argentina'),
    ('AM', 'Armenia'),
    ('AW', 'Aruba'),
    ('AU', 'Australia'),
    ('AT', 'Austria'),
    ('AZ', 'Azerbaijan'),
    ('BS', 'Bahamas'),
    ('BH', 'Bahrain'),
    ('BD', 'Bangladesh'),
    ('BB', 'Barbados'),
    ('BY', 'Belarus'),
    ('BE', 'Belgium'),
    ('BZ', 'Belize'),
    ('BJ', 'Benin'),
    ('BM', 'Bermuda'),
    ('BT', 'Bhutan'),
    ('BO', 'Bolivia, Plurinational State of'),
    ('BQ', 'Bonaire, Sint Eustatius and Saba'),
    ('BA', 'Bosnia and Herzegovina'),
    ('BW', 'Botswana'),
    ('BV', 'Bouvet Island'),
    ('BR', 'Brazil'),
    ('IO', 'British Indian Ocean Territory'),
    ('BN', 'Brunei Darussalam'),
    ('BG', 'Bulgaria'),
    ('BF', 'Burkina Faso'),
    ('BI', 'Burundi'),
    ('KH', 'Cambodia'),
    ('CM', 'Cameroon'),
    ('CA', 'Canada'),
    ('CV', 'Cape Verde'),
    ('KY', 'Cayman Islands'),
    ('CF', 'Central African Republic'),
    ('TD', 'Chad'),
    ('CL', 'Chile'),
    ('CN', 'China'),
    ('CX', 'Christmas Island'),
    ('CC', 'Cocos (Keeling) Islands'),
    ('CO', 'Colombia'),
    ('KM', 'Comoros'),
    ('CG', 'Congo'),
    ('CD', 'Congo, the Democratic Republic of the'),
    ('CK', 'Cook Islands'),
    ('CR', 'Costa Rica'),
    ('CI', 'Côte d\'Ivoire'),
    ('HR', 'Croatia'),
    ('CU', 'Cuba'),
    ('CW', 'Curaçao'),
    ('CY', 'Cyprus'),
    ('CZ', 'Czech Republic'),
    ('DK', 'Denmark'),
    ('DJ', 'Djibouti'),
    ('DM', 'Dominica'),
    ('DO', 'Dominican Republic'),
    ('EC', 'Ecuador'),
    ('EG', 'Egypt'),
    ('SV', 'El Salvador'),
    ('GQ', 'Equatorial Guinea'),
    ('ER', 'Eritrea'),
    ('EE', 'Estonia'),
    ('ET', 'Ethiopia'),
    ('FK', 'Falkland Islands (Malvinas)'),
    ('FO', 'Faroe Islands'),
    ('FJ', 'Fiji'),
    ('FI', 'Finland'),
    ('FR', 'France'),
    ('GF', 'French Guiana'),
    ('PF', 'French Polynesia'),
    ('TF', 'French Southern Territories'),
    ('GA', 'Gabon'),
    ('GM', 'Gambia'),
    ('GE', 'Georgia'),
    ('DE', 'Germany'),
    ('GH', 'Ghana'),
    ('GI', 'Gibraltar'),
    ('GR', 'Greece'),
    ('GL', 'Greenland'),
    ('GD', 'Grenada'),
    ('GP', 'Guadeloupe'),
    ('GU', 'Guam'),
    ('GT', 'Guatemala'),
    ('GG', 'Guernsey'),
    ('GN', 'Guinea'),
    ('GW', 'Guinea-Bissau'),
    ('GY', 'Guyana'),
    ('HT', 'Haiti'),
    ('HM', 'Heard Island and McDonald Islands'),
    ('VA', 'Holy See (Vatican City State)'),
    ('HN', 'Honduras'),
    ('HK', 'Hong Kong'),
    ('HU', 'Hungary'),
    ('IS', 'Iceland'),
    ('IN', 'India'),
    ('ID', 'Indonesia'),
    ('IR', 'Iran, Islamic Republic of'),
    ('IQ', 'Iraq'),
    ('IE', 'Ireland'),
    ('IM', 'Isle of Man'),
    ('IL', 'Israel'),
    ('IT', 'Italy'),
    ('JM', 'Jamaica'),
    ('JP', 'Japan'),
    ('JE', 'Jersey'),
    ('JO', 'Jordan'),
    ('KZ', 'Kazakhstan'),
    ('KE', 'Kenya'),
    ('KI', 'Kiribati'),
    ('KP', 'Korea, Democratic People\'s Republic of'),
    ('KR', 'Korea, Republic of'),
    ('KW', 'Kuwait'),
    ('KG', 'Kyrgyzstan'),
    ('LA', 'Lao People\'s Democratic Republic'),
    ('LV', 'Latvia'),
    ('LB', 'Lebanon'),
    ('LS', 'Lesotho'),
    ('LR', 'Liberia'),
    ('LY', 'Libya'),
    ('LI', 'Liechtenstein'),
    ('LT', 'Lithuania'),
    ('LU', 'Luxembourg'),
    ('MO', 'Macao'),
    ('MK', 'North-Macedonia'),
    ('MG', 'Madagascar'),
    ('MW', 'Malawi'),
    ('MY', 'Malaysia'),
    ('MV', 'Maldives'),
    ('ML', 'Mali'),
    ('MT', 'Malta'),
    ('MH', 'Marshall Islands'),
    ('MQ', 'Martinique'),
    ('MR', 'Mauritania'),
    ('MU', 'Mauritius'),
    ('YT', 'Mayotte'),
    ('MX', 'Mexico'),
    ('FM', 'Micronesia, Federated States of'),
    ('MD', 'Moldova, Republic of'),
    ('MC', 'Monaco'),
    ('MN', 'Mongolia'),
    ('ME', 'Montenegro'),
    ('MS', 'Montserrat'),
    ('MA', 'Morocco'),
    ('MZ', 'Mozambique'),
    ('MM', 'Myanmar'),
    ('NA', 'Namibia'),
    ('NR', 'Nauru'),
    ('NP', 'Nepal'),
    ('NL', 'Netherlands'),
    ('NC', 'New Caledonia'),
    ('NZ', 'New Zealand'),
    ('NI', 'Nicaragua'),
    ('NE', 'Niger'),
    ('NG', 'Nigeria'),
    ('NU', 'Niue'),
    ('NF', 'Norfolk Island'),
    ('MP', 'Northern Mariana Islands'),
    ('NO', 'Norway'),
    ('OM', 'Oman'),
    ('PK', 'Pakistan'),
    ('PW', 'Palau'),
    ('PS', 'Palestinian Territory, Occupied'),
    ('PA', 'Panama'),
    ('PG', 'Papua New Guinea'),
    ('PY', 'Paraguay'),
    ('PE', 'Peru'),
    ('PH', 'Philippines'),
    ('PN', 'Pitcairn'),
    ('PL', 'Poland'),
    ('PT', 'Portugal'),
    ('PR', 'Puerto Rico'),
    ('QA', 'Qatar'),
    ('RE', 'Réunion'),
    ('RO', 'Romania'),
    ('RU', 'Russian Federation'),
    ('RW', 'Rwanda'),
    ('BL', 'Saint Barthélemy'),
    ('SH', 'Saint Helena, Ascension and Tristan da Cunha'),
    ('KN', 'Saint Kitts and Nevis'),
    ('LC', 'Saint Lucia'),
    ('MF', 'Saint Martin (French part)'),
    ('PM', 'Saint Pierre and Miquelon'),
    ('VC', 'Saint Vincent and the Grenadines'),
    ('WS', 'Samoa'),
    ('SM', 'San Marino'),
    ('ST', 'Sao Tome and Principe'),
    ('SA', 'Saudi Arabia'),
    ('SN', 'Senegal'),
    ('RS', 'Serbia'),
    ('SC', 'Seychelles'),
    ('SL', 'Sierra Leone'),
    ('SG', 'Singapore'),
    ('SX', 'Sint Maarten (Dutch part)'),
    ('SK', 'Slovakia'),
    ('SI', 'Slovenia'),
    ('SB', 'Solomon Islands'),
    ('SO', 'Somalia'),
    ('ZA', 'South Africa'),
    ('GS', 'South Georgia and the South Sandwich Islands'),
    ('SS', 'South Sudan'),
    ('ES', 'Spain'),
    ('LK', 'Sri Lanka'),
    ('SD', 'Sudan'),
    ('SR', 'Suriname'),
    ('SJ', 'Svalbard and Jan Mayen'),
    ('SZ', 'Swaziland'),
    ('SE', 'Sweden'),
    ('CH', 'Switzerland'),
    ('SY', 'Syrian Arab Republic'),
    ('TW', 'Taiwan, Republic of China'),
    ('TJ', 'Tajikistan'),
    ('TZ', 'Tanzania, United Republic of'),
    ('TH', 'Thailand'),
    ('TL', 'Timor-Leste'),
    ('TG', 'Togo'),
    ('TK', 'Tokelau'),
    ('TO', 'Tonga'),
    ('TT', 'Trinidad and Tobago'),
    ('TN', 'Tunisia'),
    ('TR', 'Turkey'),
    ('TM', 'Turkmenistan'),
    ('TC', 'Turks and Caicos Islands'),
    ('TV', 'Tuvalu'),
    ('UG', 'Uganda'),
    ('UA', 'Ukraine'),
    ('AE', 'United Arab Emirates'),
    ('GB', 'United Kingdom'),
    ('US', 'United States'),
    ('UM', 'United States Minor Outlying Islands'),
    ('UY', 'Uruguay'),
    ('UZ', 'Uzbekistan'),
    ('VU', 'Vanuatu'),
    ('VE', 'Venezuela, Bolivarian Republic of'),
    ('VN', 'Viet Nam'),
    ('VG', 'Virgin Islands, British'),
    ('VI', 'Virgin Islands, U.S.'),
    ('WF', 'Wallis and Futuna'),
    ('EH', 'Western Sahara'),
    ('YE', 'Yemen'),
    ('ZM', 'Zambia'),
    ('ZW', 'Zimbabwe')
)
""" Names of countries and their 2-letter codes.

:type: tuple(tuple)
"""

USSTATES = (
    ('AL', 'Alabama'),
    ('AK', 'Alaska'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NY', 'New York'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PY', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming')
)
""" Names of US states and their 2-letter codes.

:type: tuple(tuple)
"""

GENDERS = (
    ('f', 'female'),
    ('m', 'male'),
    ('o', 'other')
)
""" Genders and a 1-letter abbreviation.

:type: tuple(tuple)
"""

CONTACT_METHODS = (
    (0, 'phone'),
    (1, 'email')
)
""" Available methods to contact a client.

:type: tuple(tuple)
"""

YESNO = (
    (0, 'No'),
    (1, 'Yes')
)
""" Boolean options of 'Yes' or 'No'.

This can be used to link a :class:`wtforms.fields.RadioField` form field
to a :class:`sqlalchemy.types.Boolean` database column. Use in conjunction
with :const:`BOOLIFY`.::

    name = RadioField('label', choices=YESNO, coerce=BOOLIFY)

:type: tuple(tuple)
"""

BOOLIFY = lambda x: bool(int(x))
""" Convert a number into a boolean.

A POST request always returns a string. A :class:`sqlalchemy.types.Boolean`
database column expects a Python :attr:`True` or :attr:`False` value. Use
:func:`BOOLIFY` to convert the returned string value '0' or '1' into
:attr:`False` or :attr:`True`, respectively. Use in conjunction with
:const:`YESNO`.::

    name = RadioField('label', choices=YESNO, coerce=BOOLIFY)

:type: callable
"""

DB_SERVER_TIME = text("clock_timestamp()")
"""
Postgresql specific function that returns the timestamp,
when the statement is run. It is independent of transaction time.
The function is run on the server.

:type: :meth:`sqlalchemy.text`
"""

BLOODTEST_EVAL = "SELECT public.blood_test_eval({}, {}, {});"
"""
Blood tests are evaluated (comparing the number against optimal
and normal value ranges) by calling a stored function in the
database. This constant holds the select statement to call
that function.

:type: str
"""

ALPHANUMERIC = "BCDFGHJKLMNPQRSTVWXYZ01234567890123456789"
"""
List of characters used to generated :attr:`odyssey.models.user.User.modobio_id`.
``modobio_id`` is generated by randomly chosing 12 charaters from this list.
Vowels were omitted to prevent type confusion when printed in certain fonts
(U/V, O/0, I/1 etc.).

:type: str
"""

USER_TYPES = ('staff', 'client')
"""
The general category of :class:`odyssey.models.user.User` consists of
subtypes. This constant lists the types of user supported by the
login system.

:type: tuple
"""

ACCESS_ROLES = (
    'staff_admin',
    'system_admin',
    'client_services',
    'physical_therapist',
    'trainer',
    'data_science',
    'doctor',
    'nutrition',
    'client_services_internal',
    'physical_therapist_internal',
    'trainer_internal',
    'doctor_internal',
    'nutrition_internal'
)
"""
Staff members can have a number of roles, see :attr:`odyssey.models.user.Staff.roles`.
This constant lists the roles supported by the MOdo Bio login system.

:type: tuple
"""

MEDICAL_CONDITIONS_AUTOIMMUNE = {
    'Diabetes type 1': None,
    'Diabetes type 2': None,
    'Low blood sugar/hypoglycemia': None,
    'Thyroid': {
        'Graves': None,
        'Hashimoto': None,
        'Hyperthyroid': None,
        'Hypothyroid': None
    },
    'Adrenal': {
        'Cushing\'s': None,
        'Addison\'s': None
    },
    'Thymic disease': None,
    'Multiple endocrine neoplasia (MEN) 1': None,
    'Multiple endocrine neoplasia (MEN) 2': None,
    'Rheumatoid disease': None,
    'Sjögren\'s disease': None,
    'Systemic lupus erythematosus': None,
    'Psoriatic disease': None,
    'Fibromyalgia': None,
    'Autoimmune vasculitis': None,
    'Gout': None,
    'Amyloidosis': None,
    'Sarcoidosis': None,
    'Scleroderma': None
}
"""
Lookup table for supported medical issues -- autoimmune diseases.

Implemented as a nested dicts, where the keys are the supported
(category of) medical issues. The values are either another
dict to specify a subdivision, or :attr:`None` indicating no
further nesting.

:type: dict(dict(...))
"""

MEDICAL_CONDITIONS_CANCER = {
    'Brain': None,
    'Bone': None,
    'Blood': {
        'Leukemia': None,
        'Lymphoma': None
    },
    'Gut': {
        'Esophageal': None,
        'Stomach': None,
        'Colorectal': None,
        'Liver': None,
        'Pancreatic': None
    },
    'Lung': {
        'Small cell': None,
        'Non-small cell': None
    },
    'Kidney': {
        'Renal Cell': None,
        'Urothelial carcinoma (transitional cell)': None
    },
    'Urological': {
        'Bladder': None,
        'Penile': None,
        'Prostatic': None
    },
    'Breast': None,
    'Gynecological': {
        'Cervical/ovarian': None,
        'Uterine': None,
        'Vaginal': None
    },
    'Skin': {
        'Melanoma': None,
        'Basal cell carcinoma': None,
        'Squamous cell carcinoma': None
    }
}
"""
Lookup table for supported medical issues -- cancer.

Implemented as a nested dicts, where the keys are the supported
(category of) medical issues. The values are either another
dict to specify a subdivision, or :attr:`None` indicating no
further nesting.

:type: dict(dict(...))
"""

MEDICAL_CONDITIONS_NEURO = {
    'Headaches/migraines': None,
    'Blackouts': None,
    'Dizziness/vertigo': None,
    'History of fall(s)': None,
    'Balance disturbance': None,
    'Vision loss': None,
    'Hearing loss': None,
    'Insomnia': None,
    'Traumatic head/brain injury': None,
    'Stroke/transient ischemic attack (TIA)': None,
    'Multiple sclerosis': None,
    'Peripheral neuropathy': None,
    'Guillain barre': None,
    'Myasthenia gravis': None,
    'Epilepsy/seizure disorder': None,
    'Parkinson\'s': None,
    'Alzheimer\'s dementia': None,
    'Lewy body dementia': None,
    'Other dementia or memory loss': None,
    'Spinal cord disease (disc herniation/bulging)': None,
    'Vertebral fracture or fusion': None,
    'Brain aneurysm': None,
    'Pituitary disease': None,
    'Hypothalamus disease': None,
    'Carpal tunnel': None,
    'Spinal stenosis': None,
    'Sciatica': None,
    'Spondylolisthesis': None
}
"""
Lookup table for supported medical issues -- neurological.

Implemented as a nested dicts, where the keys are the supported
(category of) medical issues. The values are either another
dict to specify a subdivision, or :attr:`None` indicating no
further nesting.

:type: dict(dict(...))
"""

MEDICAL_CONDITIONS_MUSCLE = {
    'Osteoarthritis': None,
    'Osteoporosis': None,
    'Osteopenia': None,
    'Osteomalacia': None,
    'History of fractures': {
        'Stress': None,
        'Compression': None,
        'Comminuted': None,
        'Segmental': None,
        'Spiral': None,
        'Transverse': None,
        'Oblique': None,
        'Greenstick': None,
        'Open/compound': None
    },
    'Closed': None,
    'Dislocation': None,
    'Torn ligament/meniscus/tendon': None,
    'Torn muscle': None,
    'Bone spur': None,
    'Inguinal hernia': None
}
"""
Lookup table for supported medical issues -- musculoskeletal.

Implemented as a nested dicts, where the keys are the supported
(category of) medical issues. The values are either another
dict to specify a subdivision, or :attr:`None` indicating no
further nesting.

:type: dict(dict(...))
"""

MEDICAL_CONDITIONS_CARDIO = {
    'High blood pressure (hypertension)': None,
    'Heart attack/myocardial infarction (MI)': None,
    'Congestive heart failure': None,
    'Hypertrophic cardiomyopathy': None,
    'Heart valvular disease': {
        'Aortic': None,
        'Pulmonic': None,
        'Mitral': None,
        'Tricuspid': None
    },
    'Heart murmur': None,
    'Aneurysm (aortic, or other blood vessels)': None,
    'Bleeding disorder': {
        'Hemophilia A': None,
        'Hemophilia B': None,
        'Von Willebrand\'s disease': None,
        'Rare clotting factor deficiencies': None
    },
    'Blood clots/deep venous thrombosis': {
        'Provoked': None,
        'Spontaneous': None
    },
    'Anemia': {
        'Iron deficiency': None,
        'Blood loss': None,
        'Thalassemia': None,
        'Sickle cell': None,
        'Hemolytic': None,
        'Aplastic (or other bone marrow disease)': None,
        'Megaloblastic (vitamin B12/folate deficiency)': None,
        'Pernicious': None
    },
    'Chest pain/angina': {
        'Stable': None,
        'Unstable': None
    },
    'Heart arrhythmia': {
        'Atrial fibrillation': None,
        'Atrial flutter': None,
        'Wolfe-Parkinson white': None,
        'Paroxysmal supraventricular tachycardia': None,
        'Ventricular tachycardia': None,
        'Ventricular fibrillation': None,
        'Torsades de pointes': None,
        'Premature heartbeat': None,
        'Bradycardia': None
    },
    'Pericarditis': None,
    'High cholesterol/hyperlipidemia': None,
    'Splenic disorder': None,
    'CABG/bypass surgery': None,
    'Pacemaker/defibrillator': None,
    'Vascular stents': None,
}
"""
Lookup table for supported medical issues -- cardiovascular.

Implemented as a nested dicts, where the keys are the supported
(category of) medical issues. The values are either another
dict to specify a subdivision, or :attr:`None` indicating no
further nesting.

:type: dict(dict(...))
"""

MEDICAL_CONDITIONS_KIDNEY = {
    'Chronic kidney disease': None,
    'Acute kidney failure/injury': None,
    'Pyelonephritis (kidney infection)': None,
    'Nephrolithiasis (kidney stones)': None,
    'Hydronephrosis': None,
    'Polycystic kidney disease': None,
    'Nephrotic syndrome': None,
    'Nephritic syndrome': None
}
"""
Lookup table for supported medical issues -- nephrological.

Implemented as a nested dicts, where the keys are the supported
(category of) medical issues. The values are either another
dict to specify a subdivision, or :attr:`None` indicating no
further nesting.

:type: dict(dict(...))
"""

MEDICAL_CONDITIONS = (
    ('autoimmune', MEDICAL_CONDITIONS_AUTOIMMUNE),
    ('cancer', MEDICAL_CONDITIONS_CANCER),
    ('neurological', MEDICAL_CONDITIONS_NEURO),
    ('musculoskeletal', MEDICAL_CONDITIONS_MUSCLE),
    ('cardiovascular', MEDICAL_CONDITIONS_CARDIO),
    ('nephrological', MEDICAL_CONDITIONS_KIDNEY)
)
"""
Combination of all medical disease lookup tables with a short name.
The short name should have no other characters than letters, because
it is used to derive a class name.

:type: tuple(tuple)
"""
