from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest

from odyssey import db
from odyssey.api.organizations.models import (
    OrganizationAdmins,
    OrganizationMembers,
    Organizations,
)
from odyssey.api.organizations.schemas import (
    OrganizationMembersPostInputSchema,
    OrganizationMembersPostOutputSchema,
    OrganizationsSchema,
)
from odyssey.api.user.models import User
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource

ns = Namespace("organizations", description="Endpoints for member organizations")


@ns.route("/")
class OrganizationsEndpoint(BaseResource):
    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
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
        SchemaValidationError
            If the organization name is not between 3 and 100 chars long.
        BadRequest
            If the organization owner is not a valid user.
        BadRequest
            If the organization name is already in use.
        """
        org = request.parsed_obj

        owner = db.session.get(User, org.owner)

        # Check for invalid owner
        if not owner:
            raise BadRequest("Organization owner must be a valid user.")

        # Check for duplicate organization name
        duplicate = Organizations.query.filter_by(name=org.name).one_or_none()
        if duplicate:
            raise BadRequest("Organization name already in use.")

        # Create the organization
        db.session.execute("SET CONSTRAINTS ALL DEFERRED")
        db.session.add(org)
        db.session.flush()  # Flush to get the organization_id, does not complete the transaction

        mem = OrganizationMembers(
            user_id=owner.user_id,
            organization_uuid=org.organization_uuid,
        )
        db.session.add(mem)
        db.session.flush()

        admin = OrganizationAdmins(
            user_id=mem.user_id,
            organization_uuid=org.organization_uuid,
        )
        db.session.add(admin)
        db.session.flush()

        # Update the owner foreign key from the placeholder
        org.owner = admin.user_id

        db.session.commit()  # Constraints are checked here

        # Return the organization, schema will be applied by @responds
        return org


@ns.route("/members/")
class OrganizationMembersEndpoint(BaseResource):
    @token_auth.login_required(user_type=("staff",), staff_role=("community_manager",))
    @accepts(schema=OrganizationMembersPostInputSchema, api=ns)
    @responds(schema=OrganizationMembersPostOutputSchema, api=ns, status_code=201)
    def post(self):
        """Add a list of members to an organization.

        Parameters
        ----------
        organization_uuid : uuid
            The organization to add the member to.
        members : list of ints
            A list of user_ids to add to the organization.

        Returns
        -------
        dict
            organization_uuid : uuid
                The organization the members were added to.
            added_members : list of ints
                A list of user_ids that were successfully added to the organization.
            invalid_members : list of ints
                A list of user_ids that were not added to the organization because they are not valid users.
            prior_members : list of ints


        Raises
        ------
        BadRequest
            If the organization does not exist.
        BadRequest
            If more than 100 members were provided.
        BadRequest
            If adding this many members would exceed the organization's max_members.
        """
        organization_uuid = request.json["organization_uuid"]
        members = request.json["members"]

        # Remove duplicates from members
        members = list(set(members))

        # Check for valid organization
        org = db.session.get(Organizations, organization_uuid)
        if not org:
            raise BadRequest("Organization does not exist.")

        # Check for too many members
        if len(members) > 100:
            raise BadRequest("Cannot add more than 100 members at once.")

        # Create technical maximums due to owner being admin, admins being members
        num_current_admins = OrganizationAdmins.query.filter_by(
            organization_uuid=organization_uuid,
        ).count()
        technical_max_members = 1 + num_current_admins + org.max_members
        # 1 for owner, +1 for each admin currently in org, + apparent max_members

        # Check for too many members
        num_current_members = OrganizationMembers.query.filter_by(
            organization_uuid=organization_uuid,
        ).count()
        if len(members) + num_current_members > technical_max_members:
            raise BadRequest(
                f"Adding {len(members)} members would exceed the"
                f" organization's max_members limit, {org.max_members}."
            )

        added_members = []
        invalid_members = []
        prior_members = []
        # Add the members
        for member in members:
            user = db.session.get(User, member)

            # Invalid members
            if not user:
                invalid_members.append(member)
                continue

            # Already members
            if OrganizationMembers.query.filter_by(
                user_id=member,
                organization_uuid=organization_uuid,
            ).one_or_none():
                prior_members.append(member)
                continue

            # Valid new member
            mem = OrganizationMembers(
                user_id=member,
                organization_uuid=organization_uuid,
            )
            db.session.add(mem)
            added_members.append(member)

        db.session.commit()

        # Return the organization_uuid, members added, invalid members, and prior members
        return {
            "organization_uuid": organization_uuid,
            "added_members": added_members,
            "invalid_members": invalid_members,
            "prior_members": prior_members,
        }
