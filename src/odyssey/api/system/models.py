"""
Database tables for supporting lookup tables. These tables should be static tables only used for reference,
not to be edited at runtime. 
"""

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

class SystemTelehealthSettings(db.Model):
    """ Teleheath settings that can be changed by a system administrator
    """

    __tablename__ = 'SystemTelehealthSessionCosts'

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

    territory_id = db.Column(db.Integer, db.ForeignKey('LookupCountriesOfOperations.idx'), nullable=False))
    """
    id of the territory associated with this cost.

    :type: int, foreign key('LookupCountriesOfOperations.idx')
    """

    profession_type = db.Column(db.String)
    """
    Name of the profression associated with this cost. Must be one of

    :type: string
    """

    session_cost = db.Column(db.Float)
    """
    Cost of this teleheatlh session in USD. Must be between 0 and 500.

    :type: float
    """

