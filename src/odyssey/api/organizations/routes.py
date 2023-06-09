from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.organizations.models import (
    OrganizationAdmins, OrganizationMembers, Organizations
)
from odyssey.api.organizations.schemas import OrganizationsSchema
from odyssey.api.user.models import User
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource

ns = Namespace('organizations', description='Endpoints for member organizations')


@ns.route('/')
class OrganizationsEndpoint(BaseResource):
    @token_auth.login_required(user_type=('staff', ), staff_role=('community_manager', ))
    @accepts(schema=OrganizationsSchema, api=ns)
    @responds(schema=OrganizationsSchema, api=ns, status_code=201)
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
            The user_id of the modobio user that will be the organization owner.

        Returns
        -------
        dict
            The new organization.

        Raises
        ------
        BadRequest
            If the organization owner is not a user.
        SchemaValidationError
            If the organization name is not between 3 and 100 chars long.
        BadRequest
            If the organization name is already in use.
        """
        org = request.parsed_obj

        owner = db.session.get(User, org.owner)

        # Check for invalid owner
        if not owner:
            raise BadRequest('Organization owner must be a valid user.')

        # Check for duplicate organization name
        duplicate = Organizations.query.filter_by(name=org.name).one_or_none()
        if duplicate:
            raise BadRequest('Organization name already in use.')

        # Create the organization
        db.session.execute('SET CONSTRAINTS ALL DEFERRED')
        db.session.add(org)
        db.session.flush()  # Flush to get the organization_id, does not complete the transaction

        mem = OrganizationMembers(
            user_id=owner.user_id,
            organization_id=org.organization_id,
        )
        db.session.add(mem)
        db.session.flush()

        admin = OrganizationAdmins(
            member_id=mem.member_id,
            organization_id=org.organization_id,
        )
        db.session.add(admin)
        db.session.flush()

        org.owner = admin.admin_id  # Update the owner foreign key from the placeholder

        db.session.commit()  # Constraints are checked here

        return org  # Return the organization, schema will be applied by @responds

