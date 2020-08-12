
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
    'access_role': fields.String(description=" The access role for this staff member options: ['stfappadmin' (staff application admin), 'clntsvc' (client services), 'physthera' (physiotherapist), 'datasci' (data scientist), 'doctor' (doctor), 'docext' (external doctor), 'phystrain' (physical trainer), 'nutrition' (nutritionist)]",
        enum = ['stfappadmin', 'clntsvc', 'physthera', 'phystrain', 'datasci', 'doctor', 'docext', 'nutrition']),
})

