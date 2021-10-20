import logging

logger = logging.getLogger(__name__)

from functools import wraps

from flask import request
from flask_restx import Resource
from sqlalchemy.exc import InvalidRequestError
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey.utils.auth import token_auth
from odyssey.utils.misc import find_decorator_value
from odyssey.api.user.models import User


class BaseResource(Resource):
    """
    Base endpoint to be inherited by other endpoints. Provides functions common to many endpoints

    If parsed_obj is provided, it will have reporter_id set to the logged in user's user_id
    """

    __abstract__ = True
    __check_resource__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.method_decorators = [self.check_resource]

    def check_user(self, user_id: int, user_type: str=None):
        """ Check that user ``user_id`` exists in the database.

        Fetch user with :attr:`User.user_id` from the database. It will only fetch
        not-deleted (:attr:`User.deleted` = False) users. If ``user_type``='client',
        it will additionally check that :attr:`User.is_client`=True. For ``user_type``='staff',
        :attr:`User.is_staff`=True. If ``user_type``=None, any combination of
        :attr:`User.is_client` and :attr:`User.is_staff` is accepted.

        Params
        ------
        user_id : int
            User ID number of the requested User info.

        user_type : str, optional
            Additionally check that User is a client or staff.

        Returns
        -------
        :class:`User <odyssey.api.user.models.User>`
            The User instance matching the user_id.

        Raises
        ------
        :class:`werkzeug.exceptions.BadRequest`
            HTTP 400 if the user_id does not exists in the database, is marked deleted, or fails
            the additional check requested with ``user_type``.
        """
        if user_type == 'client':
            user = User.query.filter_by(user_id=user_id, is_client=True, deleted=False).one_or_none()
        elif user_type == 'staff':
            user = User.query.filter_by(user_id=user_id, is_staff=True, deleted=False).one_or_none()
        else:
            user = User.query.filter_by(user_id=user_id, deleted=False).one_or_none()

        if not user:
            raise BadRequest(f'User {user_id} does not exist.')

        return user

    def set_reporter_id(self, parsed_obj):
        """
        Sets the reporter_id for the given parsed_obj to the currently logged in user.
        """
        parsed_obj.reporter_id = token_auth.current_user()[0].user_id

    def check_ehr_permissions(self, data):
        """
        Checks if the logged in user is the reporter for the given table row for the purpose
        of edit/delete permissions on that data.
        """
        if data.reporter_id != token_auth.current_user()[0].user_id:
            raise Unauthorized(description='Only the reporter of this record can edit or delete it.')

    def check_resource(self, func):
        """ Check whether a resource exists.

        This decorator will check for the existence of a resource before proceeding
        with the POST, PUT, or PATCH request (:attr:`func`). To determine which
        resource to check, the schema name is obtained from the :func:`@accepts`
        decorator.

        If:
        - the decorated function has a :func:`@accepts` decorator,
        - and :func:`@accepts` has a ``schema=`` parameter,
        - and the schema is generated from a database table (through :class:`marshmallow.SQLAlchemyAutoSchema`),
        - and the URL has one or more path parameters in it (e.g. `/path/<int:user_id>`),

        then:
        - the database is queried using the URL path parameters as filters,

        else:
        - nothing is done and the original function is returned.

        Following a query of the database, an error is raised if:

        1. a POST request was made and the resource already exists, or
        2. a PUT or PATCH request was made and the resource does not yet exist.

        This decorator will be applied to all HTTP methods (``get()``, ``post()``, etc.)
        by default. To **not** apply this decorator, set :attr:`__check_resource__`
        to False.::

            class SomeEndpoint(BaseResource):
                __check_resource__ = False

                @accepts(schema=SomeSchema)
                def post(self):
                    # SomeTable will _not_ be checked.
                    ...

        Params
        ------
        func : callable
            HTTP method function to wrap.

        Raises
        ------
        :class:`werkzeug.BadRequest`
            If the resource already exists for a POST request or if the resource does not
            exist for a PUT or PATCH request.
        """
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not self.__check_resource__:
                logger.debug('Not running check_resource() because __check_resource__ is False.')
                return func(*args, **kwargs)

            # Only works if URL contains one or more path arguments:
            # /some/path/<int:user_id> or similar
            if len(request.view_args) == 0:
                logger.debug(f'Not running check_resource() because no path argument in URL of {func}.')
                return func(*args, **kwargs)

            try:
                schema = find_decorator_value(func, 'accepts', keyword='schema')
            except TypeError:
                logger.debug(f'Not running check_resource() because no @accepts decorator on {func}.')
                return func(*args, **kwargs)

            if not schema:
                logger.debug(f'Not running check_resource() because no schema declared in @accepts '
                             f'decorator of {func}.')
                return func(*args, **kwargs)

            # Schema not based on a table, nothing to check.
            if not hasattr(schema.Meta, 'model'):
                logger.debug(f'Not running check_resource() because schema {schema} is not based '
                             f'on a table model.')
                return func(*args, **kwargs)

            table = schema.Meta.model
            try:
                exists = table.query.filter_by(**request.view_args).one_or_none()
            except InvalidRequestError:
                logger.debug(f'Not running check_resource() because table {table} can not be '
                             f'filtered by any of the path arguments in the URL.')
                return func(*args, **kwargs)

            if exists and request.method.lower() in ('post',):
                raise BadRequest('The resource you are trying to create (POST) already exists. '
                                 'Please use PUT or PATCH instead.')
            elif not exists and request.method.lower() in ('put', 'patch'):
                raise BadRequest('The resource you are trying to change (PUT/PATCH) does not exist. '
                                 'Please use POST first.')

            logger.debug(f'Running check_resource() for {func}.')
            return func(*args, **kwargs)
        return wrapped
