from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.organizations.models import Organizations, OrganizationAdmins, OrganizationMembers
from odyssey.api.organizations.schemas import (
    PostOrganizationInputSchema, PostOrganizationOutputSchema
)
from odyssey.api.user.models import User
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource

ns = Namespace('organizations', description='Endpoints for member organizations')


@ns.route('/')
class OrganizationsEndpoint(BaseResource):
    @token_auth.login_required(user_type=('staff', ), staff_role=('community_manager', ))
    @accepts(schema=PostOrganizationInputSchema, api=ns)
    @responds(schema=PostOrganizationOutputSchema, api=ns, status_code=201)
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
        owner : str
            The  owner of the organization. Must be a valid modobio ID or email. Must be a user.
            Owner is also an admin and member.
        owner_email_provided : bool
            Whether the owner was provided as an email or modobio ID.

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
        max_members = request.json['max_members']
        max_admins = request.json['max_admins']
        if request.json['owner_email_provided'] is True:
            owner = User.query.filter_by(email=request.json['owner']).one_or_none()
        else:
            owner = User.query.filter_by(modobio_id=request.json['owner']).one_or_none()

        # Check for invalid owner
        if not owner:
            raise BadRequest('Organization owner must be a valid user email or modobio_id.')

        # Check for invalid organization name
        if not 3 <= len(name) <= 100:
            raise BadRequest('Organization name must be between 3 and 100 chars long.')

        # Check for duplicate organization name
        duplicate = Organizations.query.filter_by(name=name).one_or_none()
        if duplicate:
            raise BadRequest('Organization name already in use.')

        # Create the organization
        db.session.execute('SET CONSTRAINTS ALL DEFERRED')
        org = Organizations(
            name=name,
            max_members=max_members,
            max_admins=max_admins,
            owner=0,  # Placeholder for the foreign key cycle, will be updated later
        )
        db.session.add(org)
        db.session.flush()

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

        org.owner = admin.admin_id

        db.session.commit()

        # Return the organization
        return org
