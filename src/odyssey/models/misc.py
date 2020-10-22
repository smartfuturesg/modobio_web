"""
Database tables for supporting miscellaneous functionality. 
"""

from odyssey import db
from odyssey.constants import DB_SERVER_TIME

class MedicalInstitutions(db.Model):
    """ Medical institutions associated with client external medical records. 
    """

    __tablename__ = 'MedicalInstitutions'

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

    institute_id = db.Column(db.Integer, primary_key=True, autoincrement=True )
    """
    medical institute id 

    :type: int, primary key, autoincrement
    """

    institute_name = db.Column(db.String, nullable=False, unique=True)
    """
    medical institution name

    :type: str
    """

class RegisteredFacilities(db.Model):
    """ Facilities registered in the modobio system. These can be internal(Modobio facilities) 
        or external(doctor's offices, hospitals, etc.)
    """

    __tablename__ = 'RegisteredFacilities'

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

    facility_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    facility id

    :type: int, primary key, autoincrement
    """

    facility_name = db.Column(db.String, nullable=False)
    """
    facility name

    :type: str
    """

    facility_address = db.Column(db.String, nullable=False, unique=True)
    """
    facility full address

    :type: str
    """

    modobio_facility = db.Column(db.Boolean)
    """
    denotes if facility is a modobio(internal) facility

    :type: bool
    """