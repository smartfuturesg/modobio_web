
from flask_restx import fields

from odyssey.api import api

DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_EXPIRATION = '%Y-%m-%d %H:%M:%S'

new_staff_member = api.model('new_staff', {
    'firstname': fields.String(description='firstname of new staff member', required=True),
    'lastname': fields.String(description='lastname of new staff member', required=True),
    'email': fields.String(description='email of new staff member', required=True),
    'password': fields.String(description='password', required=True, min_length = 6),
    'is_admin': fields.Boolean(description='T/F is this a staff admin? Should they add or remove members?', required=True),
    'is_system_admin': fields.Boolean(description='T/F this a system administrator?', required=True),
    'access_role': fields.String(description=" The access role for this staff member options: ['cs' (client services), 'pt' (physical trainer), 'data' (data scientist), 'doc' (doctor)]",
        enum = ['cs', 'pt', 'data', 'doc']),
})

pagination = api.model('pagination', {
    'page': fields.Integer(description='page requested'),
    'per-page': fields.Integer(description='per page requested'),
})

client_info =   api.model('client_info', {
            'clientid': fields.Integer(description='auto-generated client id number. Cannot be set manually'),
            'record_locator_id': fields.String(description='medical record locator id'),
            'firstname': fields.String(description=''),
            'middlename': fields.String(description=''),
            'lastname': fields.String(description=''),
            'fullname': fields.String(description=''),
            'guardianname': fields.String(description=''),
            'guardianrole': fields.String(description=''),
            'address': fields.String(description=''),
            'street': fields.String(description=''),
            'city': fields.String(description=''),
            'state': fields.String(description='', max_length=2),
            'zipcode': fields.String(description='', min_length=5, max_length=10),
            'country': fields.String(description='', max_length=2),
            'email': fields.String(description=''),
            'phone': fields.String(description='',min_length=7, max_length=12),
            'preferred': fields.Integer(description=''),
            'ringsize': fields.Float(description=''),
            'emergency_contact': fields.String(description=''),
            'emergency_phone': fields.String(description='',min_length=7, max_length=12),
            'healthcare_contact': fields.String(description=''),
            'healthcare_phone': fields.String(description='',min_length=7, max_length=12, required=False),
            'gender': fields.String(description="options: ['m', 'f', 'o' (other), 'n' (non-binary)]",enum = ['m', 'f', 'o', 'n'], max_length=1),
            'dob': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'profession': fields.String(description=''),
            'receive_docs': fields.Boolean(description='')
        })

client_signed_documents = api.model('client_signed_documents', {
    'urls': fields.List(fields.String, description='List of URLs pointing to PDF files of signed documents.')
})
