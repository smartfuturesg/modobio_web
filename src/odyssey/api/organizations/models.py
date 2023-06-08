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

    uuid = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    """
    Organization uuid.

    :type: db.UUID, primary key, default=uuid4
    """

    name = db.Column(db.String(100), nullable=False)
    """
    Organization name.
    
    :type: string, max length=100, not null
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
        db.ForeignKey('User.user_id', ondelete='RESTRICT'),
        nullable=False,
    )
    """
    Organization owner modobio_id.
    
    :type: int, foreign key to :attr:`Admins.admin_id <odyssey.api.organizations.models.Admins.admin_id>`, not null
    """

    __table_args__ = (db.UniqueConstraint('name'), )


class Members(BaseModel):
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
    
    :type: int, foreign key, not null
    """

    organization_id = db.Column(
        UUID,
        db.ForeignKey('Organizations.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    """
    Organization ID number, foreign key to :attr:`Organizations.uuid <odyssey.api.organizations.models.Organizations.uuid>`.
    
    :type: UUID, foreign key, not null
    """

    __table_args__ = (db.UniqueConstraint('user_id', 'organization_id'), )


class Admins(BaseModel):
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
        db.ForeignKey('Members.member_id', ondelete='CASCADE'),
        nullable=False,
    )
    """
    Member ID number, foreign key to :attr:`Members.member_id <odyssey.api.organizations.models.Members.member_id>`.
    
    :type: int, foreign key, not null
    """

    organization_id = db.Column(
        UUID,
        db.ForeignKey('Organizations.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    """
    Organization ID number, foreign key to :attr:`Organizations.uuid <odyssey.api.organizations.models.Organizations.uuid>`.
    
    :type: UUID, foreign key, not null
    """

    __table_args__ = (db.UniqueConstraint('member_id', 'organization_id'), )
