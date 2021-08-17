"""
Database tables for the DoseSpot's portion of the Modo Bio Staff application.
All tables in this module are prefixed with ``DoseSpot``.
"""
from sqlalchemy import text

from odyssey.utils.constants import DB_SERVER_TIME, BLOODTEST_EVAL
from odyssey import db
from odyssey.utils.base.models import BaseModel, BaseModelWithIdx, UserIdFkeyMixin, ReporterIdFkeyMixin

class DoseSpotUserID(BaseModelWithIdx, UserIdFkeyMixin):
    """ DoseSpot User ID
    
    This table is used for storing the practitioner and patients DoseSpot User ID.
    """    

    ds_user_id = db.Column(db.Integer)
    """
    DoseSpot User ID

    :type: Integer
    """

    ds_access_token = db.Column(db.String)
    """
    DoseSpot access_token 

    :type: Integer
    """    
