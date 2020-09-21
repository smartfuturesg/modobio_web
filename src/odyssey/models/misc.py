"""
Database tables for supporting miscellaneous functionality. 
"""

from odyssey import db


class MedicalInstitutions(db.Model):
    """ Medical institutions associated with client external medical records. 
    """

    __tablename__ = 'MedicalInstitutions'

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

