from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.organizations.models import Organizations
from odyssey.api.organizations.schemas import PostOrganizationSchema
from odyssey.api.user.models import User
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource

ns = Namespace('organizations', description='Endpoints for member organizations')


@ns.route('/')
@ns.doc(params={'user_id': 'User ID number'})
class OrganizationsEndpoint(BaseResource):
    @token_auth.login_required(user_type=('staff',), staff_role=('community_manager',))
    @accepts(schema=PostOrganizationSchema, api=ns)
    @responds(schema=PostOrganizationSchema, api=ns, status_code=201)
    def post(self):
        """Create a new organization.

        Parameters
        ----------
        name : str
            The name of the organization. Must be unique. Between 3 and 100 chars long, lowercase.
        max-members: int
            The maximum number of members allowed in the organization.
        max-admins: int
            The maximum number of admins allowed in the organization. All admins are members.
        owner : int
            The user ID of the owner of the organization. Must be a valid user ID.
            Owner is also an admin and member.

        Returns
        -------
        dict
            The new organization.

        Raises
        ------
        BadRequest
            If the organization name is already in use.
        BadRequest
            If the organization name is not between 3 and 100 chars long.
        BadRequest
            If the organization owner is not a user.
        """
        name = request.json['name']
        max_members = request.json['max-members']
        max_admins = request.json['max-admins']
        owner = request.json['owner']

        # Check for invalid organization name
        if not 3 <= len(name) <= 100:
            raise BadRequest('Organization name must be between 3 and 100 chars long.')

        # Check for duplicate organization name
        duplicate = Organizations.query.filter_by(name=name).one_or_none()
        if duplicate:
            raise BadRequest('Organization name already in use.')

        # Check for invalid owner
        owner = User.query.filter_by(modobio_id=owner).one_or_none()
        if not owner:
            raise BadRequest('Owner must be a valid user.')

        # Create the organization
        organization = Organizations(
            name=name,
            max_members=max_members,
            max_admins=max_admins,
            owner=owner,
        )
        db.session.add(organization)
        db.session.commit()

        # Return the organization
        return {'organization': organization}, 200
