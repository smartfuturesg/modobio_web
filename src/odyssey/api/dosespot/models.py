"""
Database tables for the DoseSpot's portion of the Modo Bio Staff application.
All tables in this module are prefixed with ``DoseSpot``.
"""
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

class DoseSpotPatientID(BaseModelWithIdx, UserIdFkeyMixin):
    """ DoseSpot Patient ID
    
    This table is used for storing the patients DoseSpot User ID.
    """    

    ds_user_id = db.Column(db.Integer)
    """
    DoseSpot User ID

    :type: Integer
    """

class DoseSpotProxyID(BaseModelWithIdx):
    """ DoseSpot Proxy USer ID

    Proxy users are necessary to do certain calls through
    DoseSpot endpoint like GET client's pharmacies or medications
    
    """
    ds_proxy_id = db.Column(db.Integer)
    """
    DoseSpot Proxy User ID

    :type: int
    """