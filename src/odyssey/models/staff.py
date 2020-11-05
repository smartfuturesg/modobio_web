"""
Database tables staff member information for the Modo Bio Staff application.
All tables in this module are prefixed with ``Staff``.
"""
from __future__ import annotations

import base64
from datetime import datetime, timedelta
import os

from werkzeug.security import generate_password_hash, check_password_hash

from odyssey import db, whooshee
from odyssey.constants import DB_SERVER_TIME

#@whooshee.register_model('firstname', 'lastname', 'email', 'phone', 'user_id')
class StaffProfile(db.Model):
    """ Staff member profile information table.

    This table stores information regarding Modo Bio
    staff member profiles.
    """
    __tablename__ = 'StaffProfile'

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    User ID number, foreign key to User.user_id

    :type: int, foreign key
    """

    membersince = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Member since date

    The date a staff member was first added to the system

    :type: datetime
    """

    bio = db.Column(db.String)
    """
    staff member profile biography

    :type: string
    """

    def set_password(self, password: str):
        """ Set hashed password in database.
        
        See :func:`werkzeug.security.generate_password_hash` for more information on how
        the password is hashed.

        Parameters
        ----------
        password : str
            The unhashed password.
        """
        self.password = generate_password_hash(password)

    def get_token(self, expires_in: int=360000) -> str:
        """ Get authorization token.

        Returns the autorization token from the database if it is not expired,
        generates a new token otherwise.

        Parameters
        ----------
        expires_in : int
            Authorization token expiration in seconds from moment of token generation.

        Returns
        -------
        str
            The valid authorization token.
        """
        now = datetime.utcnow()
        #returns current token if it is valid
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        #otherwise generate new token, add to session
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        return self.token

    def revoke_token(self):
        """ Revoke authorization token.

        Revoke authorization by setting the expiration to 1 second in the past.
        """
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        db.session.add(self)
        db.session.flush()
        db.session.commit()

    @classmethod
    def check_token(cls, token: str) -> Staff:
        """ Check if authorization token is valid.

        If the given token exists in the database and is currently valid,
        return the staff member who holds the token.

        Parameters
        ----------
        token : str
            The authorization token to be checked.

        Returns
        -------
        :class:`Staff`
            Returns the instance of :class:`Staff` that has the valid token, or None
            if the token is not valid.
        """
        staff_member = cls.query.filter_by(token=token).first()

        if staff_member is None or staff_member.token_expiration < datetime.utcnow():
            return None
        return staff_member

    def get_admin_role(self) -> str:
        """ Check whether staff member is admin or system admin.
        
        Returns
        -------
        str
            Returns ``sys_admin`` if staff member is a system admin,
            ``staff_admin`` if staff member is admin,
            or :obj:`None` otherwise.
        """
        if self.is_system_admin:
            return 'sys_admin'
        elif self.is_admin:
            return 'staff_admin'
        else:
            return None #not an admin

class ClientRemovalRequests(db.Model):
    """ Client removal request table.

    Stores the history of client removal request by staff members.
    """
    __tablename__ = 'ClientRemovalRequests'
    
    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    created_at = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Creation timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """

    updated_at = db.Column(db.DateTime, default=DB_SERVER_TIME, onupdate=DB_SERVER_TIME)
    """
    Last update timestamp of this row in the database.

    :type: :class:`datetime.datetime`
    """
    
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id', ondelete="CASCADE"), nullable=False)
    """
    Staff member user_id number, foreign key to User.user_id

    :type: int, foreign key to :attr:`User.user_id <odyssey.models.user.User.user_id>`
    """

    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Timestamp of the removal request.

    :type: :class:`datetime.datetime`, primary key
    """
