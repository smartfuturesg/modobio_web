"""
Database tables for supporting lookup tables. These tables should be static tables only used for reference,
not to be edited at runtime. 
"""

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

class SystemTelehealthSessionCosts(db.Model):
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

    territory_id = db.Column(db.Integer, db.ForeignKey('LookupCountriesOfOperations.idx'), primary_key=True, nullable=False)
    """
    id of the territory associated with this cost.

    :type: int, foreign key('LookupCountriesOfOperations.idx')
    """

    profession_type = db.Column(db.String, primary_key=True)
    """
    Name of the profression associated with this cost. Must be one of

    :type: string
    """

    session_cost = db.Column(db.Float)
    """
    Cost of this teleheatlh session in USD. Must be between 0 and 500.

    :type: float
    """

class SystemVariables(db.Model):
    """ Holds various system-wide variables that can be viewed and edited by the sys_admin.
        The value is always stored as a string and will need to be cast into its proper type where used.
    """

    __tablename__ = 'SystemVariables'

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

    var_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Id of this variable.

    :type: int, primary key, autoincrementing
    """

    var_name = db.Column(db.String)
    """
    Name of this variable.

    :type: string
    """
    
    var_value = db.Column(db.String)
    """
    Current value of this variable. Must be stored as a string and cast to the needed type in code.

    :type: string
    """