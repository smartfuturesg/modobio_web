
from flask_restx import fields

from odyssey.api import api

DATE_FORMAT = '%Y-%m-%d'

new_staff_member = api.model('new_staff', {
    'firstname': fields.String(description='firstname of new staff member', required=True),
    'lastname': fields.String(description='lastname of new staff member', required=True),
    'email': fields.String(description='email of new staff member', required=True),
    'password': fields.String(description='password', required=True),
})

pagination = api.model('pagination', {
    'page': fields.Integer(description='page requested'),
    'per-page': fields.Integer(description='per page requested'),
})

client_info =   api.model('client_info', {
            'clientid': fields.Integer(description=''),
            'firstname': fields.String(description=''),
            'middlename': fields.String(description=''),
            'lastname': fields.String(description=''),
            'fullname': fields.String(description=''),
            'guardianname': fields.String(description=''),
            'guardianrole': fields.String(description=''),
            'address': fields.String(description=''),
            'street': fields.String(description=''),
            'city': fields.String(description=''),
            'state': fields.String(description=''),
            'zipcode': fields.String(description='', min_length=5, max_length=10),
            'country': fields.String(description='', max_length=10),
            'email': fields.String(description=''),
            'phone': fields.String(description='',min_length=7, max_length=12),
            'preferred': fields.Integer(description=''),
            'ringsize': fields.Float(description=''),
            'emergency_contact': fields.String(description=''),
            'emergency_phone': fields.String(description='',min_length=7, max_length=12),
            'healthcare_contact': fields.String(description=''),
            'healthcare_phone': fields.String(description='',min_length=7, max_length=12, required=False),
            'gender': fields.String(description="options: ['m', 'f', 'o' (other), 'n' (non-binary)]",enum = ['m', 'f', 'o', 'n']),
            'dob': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'profession': fields.String(description=''),
            'receive_docs': fields.Boolean(description=''),
        })

client_consent_response = api.model('client_consent', {
    'clientid': fields.Integer(description=''),
    'infectious_disease': fields.Boolean(description='whether or not the client has a known infectious disease'),
    'signdate': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
    'signature': fields.String(description='client signature stored as a base64 encoded png image, prefixed with mime-type.'),
})

client_consent_new = api.model('client_consent', {
    'infectious_disease': fields.Boolean(description='whether or not the client has a known infectious disease'),
    'signdate': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
    'signature': fields.String(description='client signature stored as a base64 encoded png image, prefixed with mime-type.'),
})