import logging

from sqlalchemy.dialects.postgresql import UUID

from odyssey import db
from odyssey.utils.base.models import BaseModel

logger = logging.getLogger(__name__)


class Organizations(BaseModel):
    """Organization information table.

    This table stores information regarding organizations.
    """

    organization_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Organization ID.

    :type: int, primary key, autoincrement
    """

    name = db.Column(db.String(100), nullable=False)
    """
    Organization name.
    
    :type: string, max length=100, not nullable
    """

    max_members = db.Column(db.Integer, nullable=False)
    """
    Maximum number of members allowed in the organization.
    
    :type: int, not null
    """

    max_admins = db.Column(db.Integer, nullable=False)
    """
    Maximum number of admins allowed in the organization.
    
    :type: int, not null
    """

    owner = db.Column(
        db.Integer,
        db.ForeignKey('OrganizationAdmins.admin_id', ondelete='RESTRICT', deferrable=True),
        nullable=False,
    )
    """
    Organization owner modobio_id.
    
    :type: int, foreign key to :attr:`Admins.admin_id <odyssey.api.organizations.models.Admins.admin_id>`, not null
    """

    __table_args__ = (db.UniqueConstraint('name'), )


class OrganizationMembers(BaseModel):
    """Organization member information table.

    This table stores information regarding organization members.
    """

    member_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Member ID number.
    
    :type: int, primary key, autoincrement
    """

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('User.user_id', ondelete='CASCADE'),
        nullable=False,
    )
    """
    User ID number, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`.
    
    :type: int, foreign key, not nullable
    """

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey('Organizations.organization_id', ondelete='CASCADE'),
        nullable=False,
    )
    """
    Organization ID number, foreign key to :attr:`Organizations.organization_id <odyssey.api.organizations.models.Organizations.organization_id>`.
    
    :type: int, foreign key, not null
    """

    __table_args__ = (db.UniqueConstraint('user_id', 'organization_id'), )


class OrganizationAdmins(BaseModel):
    """Organization admin information table.

    This table stores information regarding organization admins.
    """

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Admin ID number.
    
    :type: int, primary key, autoincrement
    """

    member_id = db.Column(
        db.Integer,
        db.ForeignKey('OrganizationMembers.member_id', ondelete='CASCADE'),
        nullable=False,
    )
    """
    Member ID number, foreign key to :attr:`OrganizationMembers.member_id <odyssey.api.organizations.models.OrganizationMembers.member_id>`.
    
    :type: int, foreign key, not null
    """

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey('Organizations.organization_id', ondelete='CASCADE'),
        nullable=False,
    )
    """
    Organization ID number, foreign key to :attr:`Organizations.organization_id <odyssey.api.organizations.models.Organizations.organization_id>`.
    
    :type: int, foreign key, not null
    """

    __table_args__ = (db.UniqueConstraint('member_id', 'organization_id'), )
