from datetime import datetime

from flask import request, jsonify, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource, Api

from odyssey.api import api
from odyssey.constants import DOCTYPE, DOCTYPE_DOCREV_MAP
from odyssey.api.auth import token_auth, token_auth_client
from odyssey.api.errors import ClientNotFound, ContentNotFound, IllegalSetting, UserNotFound
from odyssey import db
from odyssey.pdf import to_pdf
from odyssey.models.intake import (
    ClientInfo,
    ClientConsent,
    ClientConsultContract,
    ClientIndividualContract,
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract,
    RemoteRegistration
)
from odyssey.models.doctor import MedicalHistory
from odyssey.models.pt import PTHistory
from odyssey.utils.schemas import (
    ClientInfoSchema,
    ClientConsentSchema,
    ClientConsultContractSchema,
    ClientPoliciesContractSchema,
    ClientIndividualContractSchema,
    ClientSubscriptionContractSchema,
    ClientReleaseSchema,
    MedicalHistorySchema,
    PTHistorySchema,
    SignedDocumentsSchema
) 


ns = api.namespace('remoteclient', description='Operations related to clients')



@ns.route('/clientinfo/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class RemoteClientInfo(Resource):
    """
        For getting and altering client info table as a remote client.
        Requires token authorization in addition to a valid portal id (tmp_registration)
    """
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientInfoSchema, api=ns)
    def get(self):
        """returns client info table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')

        # bring up the valid remote client. Returns None is portal is expired 
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        # check portal validity
        if not remote_client:
            raise ClientNotFound(message="Resource does not exist")

        client = ClientInfo.query.filter_by(clientid=remote_client.clientid).first()

        return client

    @accepts(schema=ClientInfoSchema, api=ns)
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientInfoSchema, api=ns)
    def put(self):
        """edit client info"""
        tmp_registration = request.args.get('tmp_registration')
        #check portal validity
        if not RemoteRegistration().check_portal_id(tmp_registration):
            raise ClientNotFound(message="Resource does not exist")

        data = request.get_json()

        client = ClientInfo.query.filter_by(email=token_auth_client.current_user().email).first()

        client.from_dict(data)
        db.session.add(client)
        db.session.commit()
        return client

@ns.route('/medicalhistory/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class MedHistory(Resource):
   
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=MedicalHistorySchema, api=ns)
    def get(self):
        """returns client's medical history as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')

        remote_client = RemoteRegistration().check_portal_id(tmp_registration)
        # check portal validity
        if not remote_client:
            raise ClientNotFound(message="Resource does not exist")
        
        client_mh = MedicalHistory.query.filter_by(clientid=remote_client.clientid).first()

        if not client_mh:
            raise ContentNotFound()

        return client_mh
    
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, status_code=201, api=ns)
    def post(self):
        """creates client's medical history and returns it as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        # bring up the valid remote client. Returns None is portal is expired 
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)
       
        # check portal validity
        if not remote_client:
            raise ClientNotFound(message="Resource does not exist")

        current_med_history = MedicalHistory.query.filter_by(clientid=remote_client.clientid).first()
        
        if current_med_history:
            raise IllegalSetting(message=f"Medical History for clientid {remote_client.clientid} already exists. Please use PUT method")

        data = request.get_json()
        data["clientid"] = remote_client.clientid

        mh_schema = MedicalHistorySchema()

        client_mh = mh_schema.load(data)

        db.session.add(client_mh)
        db.session.commit()

        return client_mh

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, api=ns)
    def put(self):
        """updates client's medical history as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')

        remote_client = RemoteRegistration().check_portal_id(tmp_registration)
       
        # check portal validity
        if not remote_client:
            raise ClientNotFound(message="Resource does not exist")

        client_mh = MedicalHistory.query.filter_by(clientid=remote_client.clientid).first()

        if not client_mh:
            raise UserNotFound(remote_client.clientid, message = f"The client with id: {remote_client.clientid} does not yet have a medical history in the database")
        
        # get payload and update the current instance followd by db commit
        data = request.get_json()
       
        data['last_examination_date'] = datetime.strptime(data['last_examination_date'], "%Y-%m-%d")
        
        client_mh.update(data)
        db.session.commit()

        return client_mh


@ns.route('/pthistory/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class ClientPTHistory(Resource):
    """GET, POST, PUT for pt history data"""
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=PTHistorySchema)
    def get(self):
        """returns most recent mobility assessment data"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        client_pt = PTHistory.query.filter_by(clientid=remote_client.clientid).first()

        if not client_pt:
            raise ContentNotFound() 
                
        return client_pt

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @accepts(schema=PTHistorySchema, api=ns)
    @responds(schema=PTHistorySchema, status_code=201, api=ns)
    def post(self):
        """returns most recent mobility assessment data"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        #check to see if there is already an entry for pt history
        current_pt_history = PTHistory.query.filter_by(clientid=remote_client.clientid).first()
        if current_pt_history:
            raise IllegalSetting(message=f"PT History for clientid {remote_client.clientid} already exists. Please use PUT method")

        data = request.get_json()
        data['clientid'] = remote_client.clientid
        
        pth_schema = PTHistorySchema()

        #create a new entry into the pt history table
        client_pt = pth_schema.load(data)

        db.session.add(client_pt)
        db.session.commit()

        return client_pt

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @accepts(schema=PTHistorySchema, api=ns)
    @responds(schema=PTHistorySchema, api=ns)
    def put(self):
        """edit user's pt history"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        #check to see if there is already an entry for pt history
        current_pt_history = PTHistory.query.filter_by(
                        clientid=remote_client.clientid).first()

        if not current_pt_history:
            raise UserNotFound(remote_client.clientid, message = f"The client with id: {remote_client.clientid} does not yet have a pt history in the database")

        
        # get payload and update the current instance followd by db commit
        data = request.get_json()

        current_pt_history.update(data)
        db.session.commit()

        return current_pt_history

    
@ns.route('/consent/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class ConsentContract(Resource):
    """client consent forms"""

    doctype = DOCTYPE.consent
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientConsentSchema, api=ns)
    def get(self):
        """returns the most recent consent table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        client_consent_form = ClientConsent.query.filter_by(clientid=remote_client.clientid).order_by(ClientConsent.idx.desc()).first()
        
        if not client_consent_form:
            raise ContentNotFound()

        return client_consent_form

    @accepts(schema=ClientConsentSchema, api=ns)
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientConsentSchema, status_code=201, api=ns)
    def post(self):
        """ Create client consent contract for the specified clientid """
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        if not remote_client:
            raise ClientNotFound(message="this client does not exist")

        data = request.get_json()
        data["clientid"] = remote_client.clientid

        client_consent_schema = ClientConsentSchema()
        client_consent_form = client_consent_schema.load(data)
        
        db.session.add(client_consent_form)
        db.session.commit()

        to_pdf(remote_client.clientid, self.doctype)
        return client_consent_form


@ns.route('/release/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class ReleaseContract(Resource):
    """Client release forms"""

    doctype = DOCTYPE.release
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientReleaseSchema, api=ns)
    def get(self):
        """returns most recent client release table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        client_release_form =  ClientRelease.query.filter_by(clientid=remote_client.clientid).order_by(ClientRelease.idx.desc()).first()

        if not client_release_form:
            raise ContentNotFound()

        return client_release_form

    @accepts(schema=ClientReleaseSchema)
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientReleaseSchema, status_code=201, api=ns)
    def post(self):
        """create client release contract object for the specified clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        if not remote_client:
            raise ClientNotFound(message="this client does not exist")

        data = request.get_json()
        data["clientid"] = remote_client.clientid
        client_release_schema = ClientReleaseSchema()
        client_release_form = client_release_schema.load(data)

        db.session.add(client_release_form)
        db.session.commit()
        to_pdf(remote_client.clientid, self.doctype)

        return client_release_form

@ns.route('/policies/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class PoliciesContract(Resource):
    """Client policies form"""

    doctype = DOCTYPE.policies
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientPoliciesContractSchema, api=ns)
    def get(self):
        """returns most recent client policies table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        client_policies =  ClientPolicies.query.filter_by(clientid=remote_client.clientid).order_by(ClientPolicies.idx.desc()).first()

        if not client_policies:
            raise ContentNotFound()

        return client_policies

    @ns.doc(security='apikey')
    @accepts(schema=ClientPoliciesContractSchema, api=ns)
    @token_auth_client.login_required
    @responds(schema=ClientPoliciesContractSchema, status_code= 201, api=ns)
    def post(self):
        """create client policies contract object for the specified clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        if not remote_client:
            raise ClientNotFound(message="this client does not exist")

        data = request.get_json()
        data["clientid"] = remote_client.clientid
        client_policies_schema = ClientPoliciesContractSchema()
        client_policies = client_policies_schema.load(data)

        db.session.add(client_policies)
        db.session.commit()
        to_pdf(remote_client.clientid, self.doctype)

        return client_policies


@ns.route('/consultcontract/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class ConsultConstract(Resource):
    """client consult contract"""

    doctype = DOCTYPE.consult
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientConsultContractSchema, api=ns)
    def get(self):
        """returns most recent client consultation table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        client_consult =  ClientConsultContract.query.filter_by(clientid=remote_client.clientid).order_by(ClientConsultContract.idx.desc()).first()

        if not client_consult:
            raise ContentNotFound()
        return client_consult

    @accepts(schema=ClientConsultContractSchema, api=ns)
    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientConsultContractSchema, status_code= 201, api=ns)
    def post(self):
        """create client consult contract object for the specified clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        if not remote_client:
            raise ClientNotFound(message="this client does not exist")

        data = request.get_json()
        data["clientid"] = remote_client.clientid
        consult_contract_schema = ClientConsultContractSchema()
        client_consult = consult_contract_schema.load(data)
        
        db.session.add(client_consult)
        db.session.commit()
        to_pdf(remote_client.clientid, self.doctype)
        return client_consult


@ns.route('/subscriptioncontract/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class SubscriptionContract(Resource):
    """client subscription contract"""

    doctype = DOCTYPE.subscription
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientSubscriptionContractSchema, api=ns)
    def get(self):
        """returns most recent client subscription contract table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        client_subscription = ClientSubscriptionContract.query.filter_by(clientid=remote_client.clientid).order_by(ClientSubscriptionContract.idx.desc()).first()

        if not client_subscription:
            raise ContentNotFound()

        return client_subscription

    @ns.doc(security='apikey')
    @accepts(schema=ClientSubscriptionContractSchema, api=ns)
    @token_auth_client.login_required
    @responds(schema=ClientSubscriptionContractSchema, status_code= 201, api=ns)
    def post(self):
        """create client subscription contract object for the specified clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        if not remote_client:
            raise ClientNotFound(message="this client does not exist")

        data = request.get_json()
        data["clientid"] = remote_client.clientid
        subscription_contract_schema = ClientSubscriptionContractSchema()
        client_subscription = subscription_contract_schema.load(data)

        db.session.add(client_subscription)
        db.session.commit()

        to_pdf(remote_client.clientid, self.doctype)

        return client_subscription

@ns.route('/servicescontract/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class IndividualContract(Resource):
    """client individual services contract"""

    doctype = DOCTYPE.individual
    docrev = DOCTYPE_DOCREV_MAP[doctype]

    @ns.doc(security='apikey')
    @token_auth_client.login_required
    @responds(schema=ClientIndividualContractSchema, api=ns)
    def get(self):
        """returns most recent client individual servies table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)
        
        client_services =  ClientIndividualContract.query.filter_by(clientid=remote_client.clientid).order_by(ClientIndividualContract.idx.desc()).first()

        if not client_services:
            raise ContentNotFound()

        return  client_services

    @token_auth_client.login_required
    @accepts(schema=ClientIndividualContractSchema, api=ns)
    @ns.doc(security='apikey')
    @responds(schema=ClientIndividualContractSchema,status_code=201, api=ns)
    def post(self):
        """create client individual services contract object for the specified clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = RemoteRegistration().check_portal_id(tmp_registration)

        if not remote_client:
            raise ClientNotFound(message="this client does not exist")

        data = request.get_json()
        data["clientid"] = remote_client.clientid

        client_services_schema = ClientIndividualContractSchema()

        client_services = client_services_schema.load(data)

        db.session.add(client_services)
        db.session.commit()

        to_pdf(remote_client.clientid, self.doctype)

        return client_services


# @ns.route('/signeddocuments/', methods=('GET',))
# @ns.doc(params={'clientid': 'Client ID number'})
# class SignedDocuments(Resource):
#     """
#     API endpoint that provides access to documents signed
#     by the client and stored as PDF files.

#     Returns
#     -------

#     Returns a list of URLs to the stored the PDF documents.
#     The URLs expire after 10 min.
#     """
#     @ns.doc(security='apikey')
#     @token_auth.login_required
#     @responds(schema=SignedDocumentsSchema, api=ns)
#     def get(self):
#         """Given a clientid, returns a list of URLs for all signed documents."""
#         tmp_registration = request.args.get('tmp_registration')
#         remote_client = RemoteRegistration().check_portal_id(tmp_registration)

#         if not remote_client:
#             raise ClientNotFound(message="this client does not exist")

#         urls = []

#         if current_app.config['DOCS_STORE_LOCAL']:
#             for table in (ClientPolicies,
#                           ClientRelease,
#                           ClientConsent,
#                           ClientConsultContract,
#                           ClientSubscriptionContract,
#                           ClientIndividualContract):
#                 result = table.query.filter_by(clientid=clientid).order_by(table.idx.desc()).first()
#                 if result and result.pdf_path:
#                     urls.append(result.pdf_path)
#         else:
#             s3 = boto3.client('s3')
#             params = {
#                 'Bucket': current_app.config['DOCS_BUCKET_NAME'],
#                 'Key': None
#             }

#             for table in (ClientPolicies,
#                           ClientRelease,
#                           ClientConsent,
#                           ClientConsultContract,
#                           ClientSubscriptionContract,
#                           ClientIndividualContract):
#                 result = table.query.filter_by(clientid=clientid).order_by(table.idx.desc()).first()
#                 if result and result.pdf_path:
#                     params['Key'] = result.pdf_path
#                     url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=600)
#                     urls.append(url)

#         return {'urls': urls}