import logging

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

from odyssey import db
from odyssey.utils.base.models import BaseModel

logger = logging.getLogger(__name__)


class Organizations(BaseModel):
    """Organization information table.

    This table stores information regarding organizations.
    """

    organization_uuid = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    """
    Organization UUID.

    :type: UUID, primary key, server default
    """

    name = db.Column(db.String(100), nullable=False)
    """
    Organization name.
    
    :type: string, max length=100, not nullable
    """

    max_members = db.Column(db.Integer, nullable=False)
    """
    Maximum number of members allowed in the organization.
    
    :type: int, not nullable
    """

    max_admins = db.Column(db.Integer, nullable=False)
    """
    Maximum number of admins allowed in the organization.
    
    :type: int, not nullable
    """

    owner = db.Column(
        db.Integer,
        db.ForeignKey('OrganizationAdmins.user_id', ondelete='RESTRICT', deferrable=True),
        nullable=False,
    )
    """
    Organization owner user_id.
    
    :type: int, foreign key to :attr:`OrganizationAdmins.user_id <odyssey.api.organizations.models.OrganizationAdmins.user_id>`, not nullable
    """

    __table_args__ = (db.UniqueConstraint('name'), )


class OrganizationMembers(BaseModel):
    """Organization member information table.

    This table stores information regarding organization members.
    """

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('User.user_id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    """
    User ID number, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`.
    
    :type: int, primary key, foreign key, not nullable
    """

    organization_uuid = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('Organizations.organization_uuid', ondelete='CASCADE'),
        nullable=False,
    )
    """
    Organization ID number, foreign key to :attr:`Organizations.organization_id <odyssey.api.organizations.models.Organizations.organization_id>`.
    
    :type: int, foreign key, not null
    """

    __table_args__ = (db.UniqueConstraint('user_id', 'organization_uuid'), )


class OrganizationAdmins(BaseModel):
    """Organization admin information table.

    This table stores information regarding organization admins.
    """

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('OrganizationMembers.user_id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    """
    Member ID number, foreign key to :attr:`OrganizationMembers.member_id <odyssey.api.organizations.models.OrganizationMembers.member_id>`.
    
    :type: int, primary key, foreign key, not null
    """

    organization_uuid = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('Organizations.organization_uuid', ondelete='CASCADE'),
        nullable=False,
    )
    """
    Organization ID number, foreign key to :attr:`Organizations.organization_id <odyssey.api.organizations.models.Organizations.organization_id>`.
    
    :type: int, foreign key, not null
    """

    __table_args__ = (db.UniqueConstraint('user_id', 'organization_uuid'), )
