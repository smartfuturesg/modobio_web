from flask import request
from flask_accepts import accepts, responds
from flask_restx import Resource

from odyssey import db
from odyssey.utils.misc import check_client_existence
from odyssey.api.payment.models import PaymentMethods
from odyssey.api.payment.schemas import PaymentMethodsSchema

ns = api.namespace('payment', description='Endpoints for functions related to payments.')

@ns.route('/<int:user_id>/')
class PaymentMethods(Resource):
    
    @token_auth.login_required(user_type=('Client',))
    @responds(schema=PaymentMethodsSchema, api=ns)
    def get(self, user_id):
        """get user payment methods"""
        check_client_existence(user_id)

        return PaymentMethods.query.filter_by(user_id=user_id).all()

    @token_auth.login_required
    @accepts(schema=PaymentMethodsSchema, api=ns)
    @responds(schema=PaymentMethodsSchema, api=ns, status_code=201)
    def post(self, user_id):
        """add a new payment method"""
        
        db.session.add(request.parsed_obj)
        db.session.commit()

        return request.parsed_obj

    