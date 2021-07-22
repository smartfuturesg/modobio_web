from flask_restx import Resource

from odyssey.utils.auth import token_auth
from odyssey.utils.misc import check_user_existence
 

class BaseResource(Resource):
    """
    Base endpoint to be inherited by other endpoints. Provides functions common to many endpoints



    If parsed_obj is provided, it will have reporter_id set to the logged in user's user_id
    """

    __abstract__ = True

    def check_user(self, user_id, user_type=None):
        """
        Checks if the given user_id is valid for the provided user_type.

        If user_type is 'client', check if user_id exists in ClientInfo table.
        If user_type is 'staff', check if user_id exists in StaffProfile table.
        If user_type is neither of the above, just check if user_id exists in User table.
        """
        check_user_existence(user_id, user_type)

    def set_reporter_id(self, parsed_obj):
        """
        Sets the reporter_id for the given parsed_obj to the currently logged in user.
        """
        parsed_obj.reporter_id = token_auth.current_user[0].user_id