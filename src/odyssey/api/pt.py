from flask import request, jsonify
from flask_restx import Resource, Api
from flask_accepts import accepts , responds

from odyssey.api.utils import check_client_existence
from odyssey.models.pt import Chessboard, PTHistory
from odyssey import db
from odyssey.api import api
from odyssey.api.auth import token_auth
from odyssey.api.errors import UserNotFound, IllegalSetting

from odyssey.api.schemas import ChessboardSchema

ns = api.namespace('pt', description='Operations related to physical therapy services')

@ns.route('/history/<int:clientid>/')
class ClientPTHistory(Resource):
    """GET, POST, PUT for pt history data"""
    @ns.doc(security='apikey')
    @token_auth.login_required
    # @ns.marshal_with(pt_history_response)
    def get(self, clientid):
        """returns most recent mobility assessment data"""
        client_pt = PTHistory.query.filter_by(
                        clientid=clientid).first()
        
        if not client_pt:
            raise UserNotFound(
                clientid=clientid, 
                message = "this client does not yet have a pt history logged")
        
        return client_pt.to_dict()

    # @ns.expect(pt_history_new, validate=True)
    @ns.doc(security='apikey')
    @token_auth.login_required
    # @ns.marshal_with(pt_history_response)
    def post(self, clientid):
        """returns most recent mobility assessment data"""
        data = request.get_json()

        #check to see if there is already an entry for pt history
        current_pt_history = PTHistory.query.filter_by(
                        clientid=clientid).first()
        # if current_pt_history:
        #     raise ResourceAlreadyExists(identification=f"clientid {clientid}")
        
        #create a new entry into the pt history table
        client_pt = PTHistory(clientid=clientid)

        client_pt.from_dict(data)

        db.session.add(client_pt)
        db.session.commit()

        return client_pt.to_dict()

    # @ns.expect(pt_history_new, validate=True)
    @ns.doc(security='apikey')
    @token_auth.login_required
    # @ns.marshal_with(pt_history_response)
    def put(self, clientid):
        """edit user's pt history"""
        data = request.get_json()

        #pull up the current pt history for the client
        client_pt = PTHistory.query.filter_by(
                        clientid=clientid).first()
        if not client_pt:
            raise UserNotFound(
                clientid=clientid, 
                message = "this client does not yet have a pt history logged")
        #prevent requests to set clientid and send message back to api user
        elif data.get('clientid', None):
            raise IllegalSetting('clientid')

        client_pt.from_dict(data)

        db.session.add(client_pt)
        db.session.commit()

        return client_pt.to_dict()

@ns.route('/chessboard/<int:clientid>/')
class ClientChessboard(Resource):
    """GET, POST for mobility assesssment data
    note that clients will have multiple entries as they progress through the program
    Trainers may update some or all fields. The backend will store every update as a new row
    fields left blank will be left as null"""
    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ChessboardSchema(many=True), api=ns)
    def get(self, clientid):
        """returns all chessboard entries for the specified client"""
        check_client_existence(clientid)

        all_entries = Chessboard.query.filter_by(clientid=clientid).order_by(Chessboard.timestamp.asc()).all()

        if len(all_entries) == 0:
            raise UserNotFound(
                clientid=clientid, 
                message = "this client does not yet have a chessboard assessment")
        
        return all_entries

    @accepts(schema=ChessboardSchema, api=ns)
    @ns.doc(security='apikey')
    @token_auth.login_required
    @responds(schema=ChessboardSchema, status_code=201, api=ns)
    def post(self, clientid):
        """create new chessboard entry"""
        check_client_existence(clientid)

        data = request.get_json()
        data['clientid'] = clientid

        chessboard_schema = ChessboardSchema()
        client_ma = chessboard_schema.load(data)
        
        db.session.add(client_ma)
        db.session.commit()

        #return the most recent entry (this one)
        most_recent =  Chessboard.query.filter_by(clientid=clientid).order_by(Chessboard.timestamp.desc()).first()

        return most_recent

