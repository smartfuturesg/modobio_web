"""
Database tables for supporting lookup tables. These tables should be static tables only used for reference,
not to be edited at runtime. 
"""
from sqlalchemy import UniqueConstraint

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

class SystemTelehealthSessionCosts(db.Model):
    """ Teleheath session costs that can be changed by a system administrator
    """

    __tablename__ = 'SystemTelehealthSessionCosts'

    __table_args__ = (UniqueConstraint(country, profession_type))

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

    cost_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    This id of this cost.

    :type: integer, primary key, autoincrementing
    """

    country = db.Column(db.String)
    """
    The country associated with this cost. Must be present in at least one entry in LookupTerritoriesOfOperation.country

    :type: string
    """

    profession_type = db.Column(db.String)
    """
    Name of the profression associated with this cost. Must be one of the ACCESS_ROLES.

    :type: string
    """

    session_cost = db.Column(db.Float)
    """
    Cost of this teleheatlh session in this country's currency.

    :type: float
    """

    session_min_cost = db.Column(db.Float)
    """
    Minimum cost allowed of this teleheatlh session in this country's currency.

    :type: float
    """
    
    session_max_cost = db.Column(db.Float)
    """
    Maximum cost allowed of this teleheatlh session in this country's currency.

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