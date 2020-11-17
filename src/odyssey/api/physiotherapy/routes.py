from flask import request
from flask_restx import Resource, Api
from flask_accepts import accepts , responds

from odyssey.api.physiotherapy.models import Chessboard, PTHistory
from odyssey import db
from odyssey.api import api
from odyssey.utils.auth import token_auth
from odyssey.utils.errors import UserNotFound, IllegalSetting, ContentNotFound
from odyssey.utils.misc import check_client_existence
from odyssey.api.physiotherapy.schemas import ChessboardSchema, PTHistorySchema

ns = api.namespace('physiotherapy', description='Operations related to physical therapy services')

@ns.route('/history/<int:user_id>/')
class ClientPTHistory(Resource):
    """GET, POST, PUT for pt history data"""
    @token_auth.login_required
    @responds(schema=PTHistorySchema)
    def get(self, user_id):
        """returns most recent pt history"""
        check_client_existence(user_id)
        client_pt = PTHistory.query.filter_by(
                        user_id=user_id).first()
        
        if not client_pt:
            raise ContentNotFound() 
                
        return client_pt

    @token_auth.login_required
    @accepts(schema=PTHistorySchema, api=ns)
    @responds(schema=PTHistorySchema, status_code=201, api=ns)
    def post(self, user_id):
        """create client's pt history"""
        check_client_existence(user_id)

        data = request.get_json()

        #check to see if there is already an entry for pt history
        current_pt_history = PTHistory.query.filter_by(
                        user_id=user_id).first()

        if current_pt_history:
            raise IllegalSetting(message=f"PT History for user_id {user_id} already exists. Please use PUT method")

        data['user_id'] = user_id
        
        #create a new entry into the pt history table
        client_pt = PTHistorySchema().load(data)

        db.session.add(client_pt)
        db.session.commit()

        return client_pt

    @token_auth.login_required
    @accepts(schema=PTHistorySchema, api=ns)
    @responds(schema=PTHistorySchema, api=ns)
    def put(self, user_id):
        """edit user's pt history"""
        check_client_existence(user_id)

        client_pt = PTHistory.query.filter_by(user_id=user_id).first()

        if not client_pt:
            raise UserNotFound(user_id, message = f"The client with id: {user_id} does not yet have a pt history in the database")

        # get payload and update the current instance followed by db commit
        data = request.get_json()

        client_pt.update(data)
        db.session.commit()

        return client_pt

@ns.route('/chessboard/<int:user_id>/')
class ClientChessboard(Resource):
    """GET, POST for chessboard assesssment data
    note that clients will have multiple entries as they progress through the program
    Trainers may update some or all fields. The backend will store every update as a new row
    fields left blank will be left as null"""
    @token_auth.login_required
    @responds(schema=ChessboardSchema(many=True), api=ns)
    def get(self, user_id):
        """returns all chessboard entries for the specified client"""
        check_client_existence(user_id)

        all_entries = Chessboard.query.filter_by(user_id=user_id).order_by(Chessboard.timestamp.asc()).all()

        if len(all_entries) == 0:
            raise ContentNotFound()
        
        return all_entries

    @accepts(schema=ChessboardSchema, api=ns)
    @token_auth.login_required
    @responds(schema=ChessboardSchema, status_code=201, api=ns)
    def post(self, user_id):
        """create new chessboard entry"""
        check_client_existence(user_id)
        
        data = request.get_json()
        data['user_id'] = user_id

        client_ma = ChessboardSchema().load(data)
        
        db.session.add(client_ma)
        db.session.commit()

        #return the most recent entry (this one)
        most_recent =  Chessboard.query.filter_by(user_id=user_id).order_by(Chessboard.timestamp.desc()).first()
        return most_recent

