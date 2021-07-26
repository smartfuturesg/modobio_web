from flask_restx import Resource

from odyssey.utils.auth import token_auth
from odyssey.utils.errors import UserNotFound
from odyssey.api.user.models import User

class BaseResource(Resource):
    """
    Base endpoint to be inherited by other endpoints. Provides functions common to many endpoints



    If parsed_obj is provided, it will have reporter_id set to the logged in user's user_id
    """

    __abstract__ = True

    def check_user(self, user_id, user_type=None):
        """Check that the user is in the database
        If user_type is 'client', check if user_id exists in ClientInfo table.
        If user_type is 'staff', check if user_id exists in StaffProfile table.
        If user_type is neither of the above, just check if user_id exists in User table.
        """
        if user_type == 'client':
            user = User.query.filter_by(user_id=user_id, is_client=True, deleted=False).one_or_none()
        elif user_type == 'staff':
            user = User.query.filter_by(user_id=user_id, is_staff=True, deleted=False).one_or_none()
        else:
            user = User.query.filter_by(user_id=user_id, deleted=False).one_or_none()
        if not user:
            raise UserNotFound(user_id)
        return user

    def set_reporter_id(self, parsed_obj):
        """
        Sets the reporter_id for the given parsed_obj to the currently logged in user.
        """
        parsed_obj.reporter_id = token_auth.current_user()[0].user_id