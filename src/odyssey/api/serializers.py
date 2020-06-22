
from flask_restx import fields

from odyssey.api import api

DATE_FORMAT = '%Y-%m-%d'

new_staff_member = api.model('new_staff', {
    'firstname': fields.String(description='firstname of new staff member', required=True),
    'lastname': fields.String(description='lastname of new staff member', required=True),
    'email': fields.String(description='email of new staff member', required=True),
    'password': fields.String(description='password', required=True, min_length = 6),
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
            'state': fields.String(description='', max_length=2),
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
            'gender': fields.String(description="options: ['m', 'f', 'o' (other), 'n' (non-binary)]",enum = ['m', 'f', 'o', 'n'], max_length=1),
            'dob': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'profession': fields.String(description=''),
            'receive_docs': fields.Boolean(description=''),
        })

client_consent = api.model('client_consent', {
    'clientid': fields.Integer(description=''),
    'infectious_disease': fields.Boolean(description='whether or not the client has a known infectious disease'),
    'signdate': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
    'signature': fields.String(description='client signature stored as a base64 encoded png image, prefixed with mime-type.'),
})

client_consent_edit = api.model('client_consent_edit', {
    'infectious_disease': fields.Boolean(description='whether or not the client has a known infectious disease'),
    'signdate': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
    'signature': fields.String(description='client signature stored as a base64 encoded png image, prefixed with mime-type.'),
})


client_release = api.model('client_release', {
            'clientid': fields.Integer(description=''),
            'release_by_other': fields.String(description = 'Describes who else can release protected health information.'),
            'release_to_other': fields.String(description = 'Describes to whom else protected health information can be released.'),
            'release_of_all': fields.Boolean(description='Indicates whether or not client want to allow to release all protected health information.'),
            'release_of_other': fields.String(description = 'Describes what other protected health information can be released.'),
            'release_date_from': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'release_date_to': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'release_purpose': fields.String(description = 'Describes for what purpose protected health information can be released.'),
            'signdate': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'signature': fields.String(description='client signature stored as a base64 encoded png image, prefixed with mime-type.')
        })

client_release_edit = api.model('client_release_edit', {
            'clientid': fields.Integer(description=''),
            'release_by_other': fields.String(description = 'Describes who else can release protected health information.'),
            'release_to_other': fields.String(description = 'Describes to whom else protected health information can be released.'),
            'release_of_all': fields.Boolean(description='Indicates whether or not client want to allow to release all protected health information.'),
            'release_of_other': fields.String(description = 'Describes what other protected health information can be released.'),
            'release_date_from': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'release_date_to': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'release_purpose': fields.String(description = 'Describes for what purpose protected health information can be released.'),
            'signdate': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'signature': fields.String(description='client signature stored as a base64 encoded png image, prefixed with mime-type.')
        })

sign_and_date = api.model('sign_and_date', {
            'clientid': fields.Integer(description=''),
            'signdate': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'signature': fields.String(description='client signature stored as a base64 encoded png image, prefixed with mime-type.')
        })

sign_and_date_edit = api.model('sign_and_date_edit', {
            'signdate': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'signature': fields.String(description='client signature stored as a base64 encoded png image, prefixed with mime-type.')
        })

client_individual_services_contract =  api.model('client_individual_services_contract',{
            'clientid': fields.Integer(description=''),
            'doctor': fields.Boolean(description='Indicates whether or not client wants doctor service.'),
            'pt': fields.Boolean(description='Indicates whether or not client wants pt service.'),
            'drinks': fields.Boolean(description='Indicates whether or not client wants super special healthy fountain of youth drinks.'),
            'data': fields.Boolean(description='Indicates whether or not client wants modobio to collect their fitness data.'),
            'signdate': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'signature': fields.String(description='client signature stored as a base64 encoded png image, prefixed with mime-type.')
        })

client_individual_services_contract_edit =  api.model('client_individual_services_contract_edit',{
            'doctor': fields.Boolean(description='Indicates whether or not client wants doctor service.'),
            'pt': fields.Boolean(description='Indicates whether or not client wants pt service.'),
            'drinks': fields.Boolean(description='Indicates whether or not client wants super special healthy fountain of youth drinks.'),
            'data': fields.Boolean(description='Indicates whether or not client wants modobio to collect their fitness data.'),
            'signdate': fields.Date(description=f'formatted as: {DATE_FORMAT}', date = DATE_FORMAT ),
            'signature': fields.String(description='client signature stored as a base64 encoded png image, prefixed with mime-type.')
        })
    
    
    
    
