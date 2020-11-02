from datetime import datetime

import boto3
from flask import request, current_app
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey.api import api
from odyssey.auth.authorize import token_auth_client
from odyssey.errors.handlers import (
    ClientNotFound, 
    ContentNotFound, 
    IllegalSetting, 
    UserNotFound
)
from odyssey import db
from odyssey.pdf import merge_pdfs, to_pdf
from odyssey.client.models import (
    ClientInfo,
    ClientConsent,
    ClientConsultContract,
    ClientIndividualContract,
    ClientPolicies,
    ClientRelease,
    ClientSubscriptionContract
)
from odyssey.doctor.models import MedicalHistory
from odyssey.pt.models import PTHistory
from odyssey.trainer.models import FitnessQuestionnaire
from odyssey.utils.misc import check_remote_client_portal_validity
from odyssey.doctor.schemas import (
    MedicalHistorySchema
)
from odyssey.trainer.schemas import (
    FitnessQuestionnaireSchema
)
from odyssey.client.schemas import (
    ClientInfoSchema,
    ClientConsentSchema,
    ClientConsultContractSchema,
    ClientPoliciesContractSchema,
    ClientIndividualContractSchema,
    ClientSubscriptionContractSchema,
    ClientReleaseSchema,
    SignedDocumentsSchema
)
from odyssey.pt.schemas import PTHistorySchema


ns = api.namespace('remoteclient', description='Operations related to clients')



@ns.route('/clientinfo/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class RemoteClientInfo(Resource):
    """
        For getting and altering client info table as a remote client.
        Requires token authorization in addition to a valid portal id (tmp_registration)
    """
    @token_auth_client.login_required
    @responds(schema=ClientInfoSchema, api=ns)
    def get(self):
        """returns client info table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        # bring up the valid remote client. Raise error if  None is portal is expired
        remote_client = check_remote_client_portal_validity(tmp_registration)

        client = ClientInfo.query.filter_by(clientid=remote_client.clientid).first()

        return client

    @accepts(schema=ClientInfoSchema, api=ns)
    @token_auth_client.login_required
    @responds(schema=ClientInfoSchema, api=ns)
    def put(self):
        """edit client info"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        data = request.get_json()

        client = ClientInfo.query.filter_by(clientid=remote_client.clientid).first()

        client.update(data)
        db.session.commit()
        return client

@ns.route('/medicalhistory/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class MedHistory(Resource):
    @token_auth_client.login_required
    @responds(schema=MedicalHistorySchema, api=ns)
    def get(self):
        """returns client's medical history as a json for the clientid specified. Clientid is found by first pulling up the remoteclient entry"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        client_mh = MedicalHistory.query.filter_by(clientid=remote_client.clientid).first()

        if not client_mh:
            raise ContentNotFound()

        return client_mh

    @token_auth_client.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, status_code=201, api=ns)
    def post(self):
        """creates client's medical history and returns it as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        # bring up the valid remote client. Returns None is portal is expired 
        remote_client = check_remote_client_portal_validity(tmp_registration)

        # ensure client has not already submitted a medical history
        current_med_history = MedicalHistory.query.filter_by(clientid=remote_client.clientid).first()
        
        if current_med_history:
            raise IllegalSetting(message=f"Medical History for clientid {remote_client.clientid} already exists. Please use PUT method")

        data = request.get_json()
        data["clientid"] = remote_client.clientid

        client_mh = MedicalHistorySchema().load(data)

        db.session.add(client_mh)
        db.session.commit()

        return client_mh

    @token_auth_client.login_required
    @accepts(schema=MedicalHistorySchema, api=ns)
    @responds(schema=MedicalHistorySchema, api=ns)
    def put(self):
        """updates client's medical history as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

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
    @token_auth_client.login_required
    @responds(schema=PTHistorySchema)
    def get(self):
        """returns most recent mobility assessment data"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        client_pt = PTHistory.query.filter_by(clientid=remote_client.clientid).first()

        if not client_pt:
            raise ContentNotFound() 
                
        return client_pt

    @token_auth_client.login_required
    @accepts(schema=PTHistorySchema, api=ns)
    @responds(schema=PTHistorySchema, status_code=201, api=ns)
    def post(self):
        """returns most recent mobility assessment data"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        #check to see if there is already an entry for pt history
        current_pt_history = PTHistory.query.filter_by(clientid=remote_client.clientid).first()
        if current_pt_history:
            raise IllegalSetting(message=f"PT History for clientid {remote_client.clientid} already exists. Please use PUT method")

        data = request.get_json()
        data['clientid'] = remote_client.clientid
        
        #create a new entry into the pt history table
        client_pt = PTHistorySchema().load(data)

        db.session.add(client_pt)
        db.session.commit()

        return client_pt

    @token_auth_client.login_required
    @accepts(schema=PTHistorySchema, api=ns)
    @responds(schema=PTHistorySchema, api=ns)
    def put(self):
        """edit user's pt history"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        #check to see if there is already an entry for pt history
        current_pt_history = PTHistory.query.filter_by(
                        clientid=remote_client.clientid).first()

        if not current_pt_history:
            raise UserNotFound(remote_client.clientid, message = f"The client with id: {remote_client.clientid} does not yet have a pt history in the database")
        
        # get payload and update the current instance followed by db commit
        data = request.get_json()

        current_pt_history.update(data)
        db.session.commit()

        return current_pt_history

    
@ns.route('/consent/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class ConsentContract(Resource):
    """client consent forms"""

    @token_auth_client.login_required
    @responds(schema=ClientConsentSchema, api=ns)
    def get(self):
        """returns the most recent consent table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        client_consent_form = ClientConsent.query.filter_by(clientid=remote_client.clientid).order_by(ClientConsent.idx.desc()).first()
        
        if not client_consent_form:
            raise ContentNotFound()

        return client_consent_form

    @accepts(schema=ClientConsentSchema, api=ns)
    @token_auth_client.login_required
    @responds(schema=ClientConsentSchema, status_code=201, api=ns)
    def post(self):
        """ Create client consent contract for the specified clientid """
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        data = request.get_json()
        data["clientid"] = remote_client.clientid

        client_consent_form = ClientConsentSchema().load(data)
        client_consent_form.revision = ClientConsent.current_revision
        
        db.session.add(client_consent_form)
        db.session.commit()

        to_pdf(remote_client.clientid, ClientConsent)

        return client_consent_form


@ns.route('/release/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class ReleaseContract(Resource):
    """Client release forms"""

    @token_auth_client.login_required
    @responds(schema=ClientReleaseSchema, api=ns)
    def get(self):
        """returns most recent client release table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        client_release_form =  ClientRelease.query.filter_by(clientid=remote_client.clientid).order_by(ClientRelease.idx.desc()).first()

        if not client_release_form:
            raise ContentNotFound()

        return client_release_form

    @accepts(schema=ClientReleaseSchema)
    @token_auth_client.login_required
    @responds(schema=ClientReleaseSchema, status_code=201, api=ns)
    def post(self):
        """create client release contract object for the specified clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        if not remote_client:
            raise ClientNotFound(message="this client does not exist")

        data = request.get_json()
        data["clientid"] = remote_client.clientid
        client_release_form = ClientReleaseSchema().load(data)
        client_release_form.revision = ClientRelease.current_revision

        db.session.add(client_release_form)
        db.session.commit()
        to_pdf(remote_client.clientid, ClientRelease)

        return client_release_form

@ns.route('/policies/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class PoliciesContract(Resource):
    """Client policies form"""

    @token_auth_client.login_required
    @responds(schema=ClientPoliciesContractSchema, api=ns)
    def get(self):
        """returns most recent client policies table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        client_policies =  ClientPolicies.query.filter_by(clientid=remote_client.clientid).order_by(ClientPolicies.idx.desc()).first()

        if not client_policies:
            raise ContentNotFound()

        return client_policies

    @accepts(schema=ClientPoliciesContractSchema, api=ns)
    @token_auth_client.login_required
    @responds(schema=ClientPoliciesContractSchema, status_code= 201, api=ns)
    def post(self):
        """create client policies contract object for the specified clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        if not remote_client:
            raise ClientNotFound(message="this client does not exist")

        data = request.get_json()
        data["clientid"] = remote_client.clientid
        client_policies = ClientPoliciesContractSchema().load(data)
        client_policies.revision = ClientPolicies.current_revision

        db.session.add(client_policies)
        db.session.commit()
        to_pdf(remote_client.clientid, ClientPolicies)

        return client_policies


@ns.route('/consultcontract/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class ConsultConstract(Resource):
    """client consult contract"""

    @token_auth_client.login_required
    @responds(schema=ClientConsultContractSchema, api=ns)
    def get(self):
        """returns most recent client consultation table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        client_consult =  ClientConsultContract.query.filter_by(clientid=remote_client.clientid).order_by(ClientConsultContract.idx.desc()).first()

        if not client_consult:
            raise ContentNotFound()

        return client_consult

    @accepts(schema=ClientConsultContractSchema, api=ns)
    @token_auth_client.login_required
    @responds(schema=ClientConsultContractSchema, status_code= 201, api=ns)
    def post(self):
        """create client consult contract object for the specified clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        data = request.get_json()
        data["clientid"] = remote_client.clientid
        client_consult = ClientConsultContractSchema().load(data)
        client_consult.revision = ClientConsultContract.current_revision
        
        db.session.add(client_consult)
        db.session.commit()
        to_pdf(remote_client.clientid, ClientConsultContract)

        return client_consult


@ns.route('/subscriptioncontract/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class SubscriptionContract(Resource):
    """client subscription contract"""

    @token_auth_client.login_required
    @responds(schema=ClientSubscriptionContractSchema, api=ns)
    def get(self):
        """returns most recent client subscription contract table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        client_subscription = ClientSubscriptionContract.query.filter_by(clientid=remote_client.clientid).order_by(ClientSubscriptionContract.idx.desc()).first()

        if not client_subscription:
            raise ContentNotFound()

        return client_subscription

    @accepts(schema=ClientSubscriptionContractSchema, api=ns)
    @token_auth_client.login_required
    @responds(schema=ClientSubscriptionContractSchema, status_code= 201, api=ns)
    def post(self):
        """create client subscription contract object for the specified clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        data = request.get_json()
        data["clientid"] = remote_client.clientid
        subscription_contract_schema = ClientSubscriptionContractSchema()
        client_subscription = subscription_contract_schema.load(data)
        client_subscription.revision = ClientSubscriptionContract.current_revision

        db.session.add(client_subscription)
        db.session.commit()

        to_pdf(remote_client.clientid, ClientSubscriptionContract)

        return client_subscription

@ns.route('/servicescontract/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class IndividualContract(Resource):
    """client individual services contract"""

    @token_auth_client.login_required
    @responds(schema=ClientIndividualContractSchema, api=ns)
    def get(self):
        """returns most recent client individual servies table as a json for the clientid specified"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        client_services =  ClientIndividualContract.query.filter_by(clientid=remote_client.clientid).order_by(ClientIndividualContract.idx.desc()).first()

        if not client_services:
            raise ContentNotFound()

        return  client_services

    @token_auth_client.login_required
    @accepts(schema=ClientIndividualContractSchema, api=ns)
    @responds(schema=ClientIndividualContractSchema,status_code=201, api=ns)
    def post(self):
        """create client individual services contract object for the specified clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        data = request.get_json()
        data["clientid"] = remote_client.clientid

        client_services = ClientIndividualContractSchema().load(data)
        client_services.revision = ClientIndividualContract.current_revision

        db.session.add(client_services)
        db.session.commit()

        to_pdf(remote_client.clientid, ClientIndividualContract)

        return client_services


@ns.route('/signeddocuments/', methods=('GET',))
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class SignedDocuments(Resource):
    """
    API endpoint that provides access to documents signed
    by the client and stored as PDF files.

    Returns
    -------

    Returns a list of URLs to the stored the PDF documents.
    The URLs expire after 10 min.
    """
    @token_auth_client.login_required
    @responds(schema=SignedDocumentsSchema, api=ns)
    def get(self):
        """ Given a clientid, returns a dict of URLs for all signed documents.

        Parameters
        ----------
        clientid : int
            Client ID number

        Returns
        -------
        dict
            Keys are the display names of the documents,
            values are URLs to the generated PDF documents.
        """
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        urls = {}
        paths = []

        if not current_app.config['LOCAL_CONFIG']:
            s3 = boto3.client('s3')
            params = {
                'Bucket': current_app.config['S3_BUCKET_NAME'],
                'Key': None
            }

        for table in (
            ClientPolicies,
            ClientConsent,
            ClientRelease,
            ClientConsultContract,
            ClientSubscriptionContract,
            ClientIndividualContract
        ):
            result = (
                table.query
                .filter_by(clientid=remote_client.clientid)
                .order_by(table.idx.desc())
                .first()
            )
            if result and result.pdf_path:
                paths.append(result.pdf_path)
                if not current_app.config['LOCAL_CONFIG']:
                    params['Key'] = result.pdf_path
                    url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=600)
                    urls[table.displayname] = url
                else:
                    urls[table.displayname] = result.pdf_path

        concat = merge_pdfs(paths, remote_client.clientid)
        urls['All documents'] = concat

        return {'urls': urls}


@ns.route('/questionnaire/')
@ns.doc(params={'tmp_registration': 'temporary registration portal hash'})
class InitialQuestionnaire(Resource):    
    """GET and POST initial fitness questionnaire"""
    @token_auth_client.login_required
    @responds(schema=FitnessQuestionnaireSchema, api=ns)
    def get(self):
        """returns client's most recent fitness questionnaire"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        client_fq = FitnessQuestionnaire.query.filter_by(clientid=remote_client.clientid).order_by(FitnessQuestionnaire.idx.desc()).first()

        if not client_fq:
            raise ContentNotFound()
        
        return client_fq

    @token_auth_client.login_required
    @accepts(schema=FitnessQuestionnaireSchema, api=ns)
    @responds(schema=FitnessQuestionnaireSchema, status_code=201, api=ns)
    def post(self):
        """create a fitness questionnaire entry for clientid"""
        tmp_registration = request.args.get('tmp_registration')
        remote_client = check_remote_client_portal_validity(tmp_registration)

        data=request.get_json()
        data['clientid'] = remote_client.clientid

        client_fq = FitnessQuestionnaireSchema().load(data)
        
        db.session.add(client_fq)
        db.session.commit()
        
        return client_fq