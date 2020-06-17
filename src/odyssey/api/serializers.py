
from flask_restx import fields

from odyssey.api import api


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
            'client_id': fields.Integer(description=''),
            'first_name': fields.String(description=''),
            'last_name': fields.String(description=''),
            'full_name': fields.String(description=''),
            'guardian_name': fields.String(description=''),
            'guardian_role': fields.String(description=''),
            'address': fields.String(description=''),
            'street': fields.String(description=''),
            'city': fields.String(description=''),
            'state': fields.String(description=''),
            'zipcode': fields.String(description='', min_length=5, max_length=10),
            'country': fields.String(description='', max_length=10),
            'email': fields.String(description=''),
            'phone': fields.String(description='',min_length=7, max_length=11),
            'preferred': fields.Integer(description=''),
            'ring_size': fields.Float(description=''),
            'emergency_contact': fields.String(description=''),
            'emergency_phone': fields.String(description='',min_length=7, max_length=11),
            'healthcare_contact': fields.String(description=''),
            'healthcare_phone': fields.String(description='',min_length=7, max_length=11),
            'gender': fields.String(description="options: ['m', 'f', 'o' (other), 'nb' (non-binary)]",enum = ['m', 'f', 'o', 'nb']),
            'dob': fields.Date(description=''),
            'profession': fields.String(description=''),
            'receive_docs': fields.Boolean(description=''),
        })