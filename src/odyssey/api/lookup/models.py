"""
Database tables for supporting lookup tables. These tables should be static tables only used for reference,
not to be edited at runtime. 
"""

from odyssey import db
from odyssey.utils.constants import DB_SERVER_TIME

class LookupDrinks(db.Model):
    """ Static list of drinks that a client can purchase or be recommended. 
    """

    __tablename__ = 'LookupDrinks'

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

    drink_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique id for this drink.

    :type: int, primary key, autoincrement
    """

    goal_name = db.Column(db.String)
    """
    Name of the goal.

    :type: string
    """

class LookupDrinkIngredients(db.Model):
    """ List of ingredients that a drink is made up of. 
    """

    __tablename__ = 'LookupDrinkIngredients'

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

    drink_id = db.Column(db.Integer, db.ForeignKey('LookupDrinks.drink_id'))

    ingredient_name = db.Column(db.String)
    """
    Name of the ingredient.

    :type: string
    """

    amount = db.Column(db.Float)
    """
    Numerical value of the measurement.

    :type: float
    """

    unit = db.Column(db.String)
    """
    Unit of the measurement.

    :type: string
    """

class LookupGoals(db.Model):
    """ Static list of goals that a client can choose from. 
    """

    __tablename__ = 'LookupGoals'

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

    drink_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Unique id for this drink.

    :type: int, primary key, autoincrement
    """

    primary_goal = db.Column(db.Integer, db.ForeignKey('LookupGoals.idx', ondelete="CASCADE"), nullable=False)
    """
    Primary user goal that this supplement helps to meet.

    :type: int, foreign key(LookupGoals.idx)
    """

    primary_ingredient
    """
    Primary ingredient making up this drink.

    :type: string
    """

    color
    """
    Color of this drink.

    :type: string
    """

    key_additivies
    """
    Key additives in this drink.

    :type: string
    """

    

    