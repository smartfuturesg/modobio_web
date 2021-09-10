"""
Database tables for the DoseSpot's portion of the Modo Bio Staff application.
All tables in this module are prefixed with ``DoseSpot``.
"""
from sqlalchemy import text

from odyssey.utils.constants import DB_SERVER_TIME, BLOODTEST_EVAL
from odyssey import db
from odyssey.utils.base.models import BaseModel, BaseModelWithIdx, UserIdFkeyMixin, ReporterIdFkeyMixin

class DoseSpotPractitionerID(BaseModelWithIdx, UserIdFkeyMixin):
    """ DoseSpot Practitioner ID
    
    This table is used for storing the practitioner DoseSpot User ID.
    """    

    ds_user_id = db.Column(db.Integer)
    """
    DoseSpot User ID

    :type: Integer
    """

    ds_enrollment_status = db.Column(db.String)
    """
    Enrollment status <enrolled, pending, rejected>

    :type: str
    """

    ds_encrypted_user_id = db.Column(db.String)
    """
    Encrypted user ID for DoseSpot

    :type: str
    """
    

class DoseSpotPatientID(BaseModelWithIdx, UserIdFkeyMixin):
    """ DoseSpot User ID
    
    This table is used for storing the patients DoseSpot User ID.
    """    

    ds_user_id = db.Column(db.Integer)
    """
    DoseSpot User ID

    :type: Integer
    """