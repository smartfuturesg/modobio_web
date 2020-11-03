"""
Database tables for the physical therapist's portion of the Modo Bio Staff application.
All tables in this module are prefixed with ``PT``.
"""

from odyssey import db
from odyssey.constants import DB_SERVER_TIME


class PTHistory(db.Model):
    """ Physical therapy history table.

    This table stores the physical therapy history of a client. The information
    is taken only once, during the initial consult.
    """

    __tablename__ = 'PTHistory'

    displayname = 'Physical therapy history'

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

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='PTHistory_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid <odyssey.models.client.ClientInfo.clientid>`
    """

    exercise = db.Column(db.Text)
    """
    Description of the client's current exercise schedule.

    :type: str
    """

    has_pt = db.Column(db.Boolean)
    """
    Indicates whether or not client has had physical therapy in the past.

    :type: bool
    """

    has_chiro = db.Column(db.Boolean)
    """
    Indicates whether or not client has had chiropractor therapy in the past.

    :type: bool
    """

    has_massage = db.Column(db.Boolean)
    """
    Indicates whether or not client has had massage therapy in the past.

    :type: bool
    """

    has_surgery = db.Column(db.Boolean)
    """
    Indicates whether or not client has had surgery in the past.

    :type: bool
    """

    has_medication = db.Column(db.Boolean)
    """
    Indicates whether or not client uses any type of medication.

    :type: bool
    """

    has_acupuncture = db.Column(db.Boolean)
    """
    Indicates whether or not client has had acupuncture in the past.

    :type: bool
    """

    pain_areas = db.Column(db.Text)
    """
    Describes pain areas in the client's body.

    The client or staff member indicates pain areas by drawing on the silhouette
    of a human (front and back) and circling the pain areas. The drawings are
    translated to bezier curves in canvas coordinates, which are stored as a
    JSON dictionary.

    :type: str
    """

    best_pain = db.Column(db.Integer)
    """
    Numerical score of client's best pain level.

    :type: int
    """

    worst_pain = db.Column(db.Integer)
    """
    Numerical score of client's worst pain level.

    :type: int
    """
    
    current_pain = db.Column(db.Integer)
    """
    Numerical score of client's current pain level.

    :type: int
    """

    makes_worse = db.Column(db.String(1024))
    """
    Description of factors that make client's pain worse.

    :type: str, max length 1024
    """

    makes_better = db.Column(db.String(1024))
    """
    Description of factors that make client's pain better.

    :type: str, max length 1024
    """


class Chessboard(db.Model):
    """ Mobility assessment table a.k.a the chessboard.

    This table stores the repeated mobility assessment measurements.
    """

    __tablename__ = 'PTChessboard'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='chessboard_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid <odyssey.models.client.ClientInfo.clientid>`
    """

    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Timestamp of the assessment.

    :type: :class:`datetime.datetime`
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

    isa_structure = db.Column(db.String(24))
    """
    Structure of the Infrasternal Angle (ISA). Allowed values are:

    - inhaled
    - exhaled
    - asymmetrical normal
    - asymmetrical atypical

    :type: str, max length 24
    """

    isa_movement = db.Column(db.String(24))
    """
    Movement of the Infrasternal Angle (ISA). Allowed values are:

    - static
    - dynamic
    - left static/right dynamic
    - left dynamic/right static

    :type: str, max length 24
    """

    left_shoulder_er = db.Column(db.Integer)
    """
    Left shoulder external rotation angle.

    :type: int
    :unit: degree
    """

    left_shoulder_ir = db.Column(db.Integer)
    """
    Left shoulder internal rotation angle.

    :type: int
    :unit: degree
    """

    left_shoulder_abd = db.Column(db.Integer)
    """
    Left shoulder abduction angle.

    :type: int
    :unit: degree
    """

    left_shoulder_add = db.Column(db.Integer)
    """
    Left shoulder adduction angle.

    :type: int
    :unit: degree
    """

    left_shoulder_flexion = db.Column(db.Integer)
    """
    Left shoulder flexion angle.

    :type: int
    :unit: degree
    """

    left_shoulder_extension = db.Column(db.Integer)
    """
    Left shoulder extension angle.

    :type: int
    :unit: degree
    """

    right_shoulder_er = db.Column(db.Integer)
    """
    Right shoulder external rotation angle.

    :type: int
    :unit: degree
    """

    right_shoulder_ir = db.Column(db.Integer)
    """
    Right shoulder internal rotation angle.

    :type: int
    :unit: degree
    """

    right_shoulder_abd = db.Column(db.Integer)
    """
    Right shoulder abduction angle.

    :type: int
    :unit: degree
    """

    right_shoulder_add = db.Column(db.Integer)
    """
    Right shoulder adduction angle.

    :type: int
    :unit: degree
    """

    right_shoulder_flexion = db.Column(db.Integer)
    """
    Right shoulder flexion angle.

    :type: int
    :unit: degree
    """

    right_shoulder_extension = db.Column(db.Integer)
    """
    Right shoulder extension angle.

    :type: int
    :unit: degree
    """

    left_hip_er = db.Column(db.Integer)
    """
    Left hip external rotation angle.

    :type: int
    :unit: degree
    """

    left_hip_ir = db.Column(db.Integer)
    """
    Left hip internal rotation angle.

    :type: int
    :unit: degree
    """

    left_hip_abd = db.Column(db.Integer)
    """
    Left hip abduction angle.

    :type: int
    :unit: degree
    """

    left_hip_add = db.Column(db.Integer)
    """
    Left hip adduction angle.

    :type: int
    :unit: degree
    """

    left_hip_flexion = db.Column(db.Integer)
    """
    Left hip flexion angle.

    :type: int
    :unit: degree
    """

    left_hip_extension = db.Column(db.Integer)
    """
    Left hip extension angle.

    :type: int
    :unit: degree
    """

    left_hip_slr = db.Column(db.Integer)
    """
    Left hip straight leg raise angle.

    :type: int
    :unit: degree
    """

    right_hip_er = db.Column(db.Integer)
    """
    Right hip external rotation angle.

    :type: int
    :unit: degree
    """

    right_hip_ir = db.Column(db.Integer)
    """
    Right hip internal rotation angle.

    :type: int
    :unit: degree
    """

    right_hip_abd = db.Column(db.Integer)
    """
    Right hip abduction angle.

    :type: int
    :unit: degree
    """

    right_hip_add = db.Column(db.Integer)
    """
    Right hip adduction angle.

    :type: int
    :unit: degree
    """

    right_hip_flexion = db.Column(db.Integer)
    """
    Right hip flexion angle.

    :type: int
    :unit: degree
    """

    right_hip_extension = db.Column(db.Integer)
    """
    Right hip extension angle.

    :type: int
    :unit: degree
    """

    right_hip_slr = db.Column(db.Integer)
    """
    Right hip straight leg raise angle.

    :type: int
    :unit: degree
    """

    notes = db.Column(db.Text)
    """
    Assessment notes.

    :type: str
    """

class MobilityAssessment(db.Model):
    """ Mobility assessment table.

    The previous version of the mobility assessment table.
    Superceded by :class:`Chessboard`.

    .. deprecated:: v0.0.3

    .. seealso:: :class:`Chessboard`
    """

    __tablename__ = 'MobilityAssessment'

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'),
                        nullable=False, primary_key=True)
    """
    Client ID number.

    :type: int, foreign key to :attr:`ClientInfo.clientid <odyssey.models.client.ClientInfo.clientid>`
    """

    timestamp = db.Column(db.DateTime, default=DB_SERVER_TIME)
    """
    Timestamp of the assessment.

    :type: :class:`datetime.datetime`
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

    isa_left = db.Column(db.Integer)
    """
    Infasternal angle (ISA) left.

    :type: int
    :unit: degree
    """

    isa_right = db.Column(db.Integer)
    """
    Infasternal angle (ISA) right.

    :type: int
    :unit: degree
    """

    isa_dynamic = db.Column(db.Boolean)
    """
    Indicates whether or not the Infasternal angle (ISA) is dynamic.

    :type: bool
    """

    left_shoulder_er = db.Column(db.Integer)
    """
    Left shoulder external rotation angle.

    :type: int
    :unit: degree
    """

    left_shoulder_ir = db.Column(db.Integer)
    """
    Left shoulder internal rotation angle.

    :type: int
    :unit: degree
    """

    left_shoulder_abd = db.Column(db.Integer)
    """
    Left shoulder abduction angle.

    :type: int
    :unit: degree
    """

    left_shoulder_add = db.Column(db.Integer)
    """
    Left shoulder adduction angle.

    :type: int
    :unit: degree
    """

    left_shoulder_flexion = db.Column(db.Integer)
    """
    Left shoulder flexion angle.

    :type: int
    :unit: degree
    """

    left_shoulder_extension = db.Column(db.Integer)
    """
    Left shoulder extension angle.

    :type: int
    :unit: degree
    """

    right_shoulder_er = db.Column(db.Integer)
    """
    Right shoulder external rotation angle.

    :type: int
    :unit: degree
    """

    right_shoulder_ir = db.Column(db.Integer)
    """
    Right shoulder internal rotation angle.

    :type: int
    :unit: degree
    """

    right_shoulder_abd = db.Column(db.Integer)
    """
    Right shoulder abduction angle.

    :type: int
    :unit: degree
    """

    right_shoulder_add = db.Column(db.Integer)
    """
    Right shoulder adduction angle.

    :type: int
    :unit: degree
    """

    right_shoulder_flexion = db.Column(db.Integer)
    """
    Right shoulder flexion angle.

    :type: int
    :unit: degree
    """

    right_shoulder_extension = db.Column(db.Integer)
    """
    Right shoulder extension angle.

    :type: int
    :unit: degree
    """

    left_hip_er = db.Column(db.Integer)
    """
    Left hip external rotation angle.

    :type: int
    :unit: degree
    """

    left_hip_ir = db.Column(db.Integer)
    """
    Left hip internal rotation angle.

    :type: int
    :unit: degree
    """

    left_hip_abd = db.Column(db.Integer)
    """
    Left hip abduction angle.

    :type: int
    :unit: degree
    """

    left_hip_add = db.Column(db.Integer)
    """
    Left hip adduction angle.

    :type: int
    :unit: degree
    """

    left_hip_flexion = db.Column(db.Integer)
    """
    Left hip flexion angle.

    :type: int
    :unit: degree
    """

    left_hip_extension = db.Column(db.Integer)
    """
    Left hip extension angle.

    :type: int
    :unit: degree
    """

    right_hip_er = db.Column(db.Integer)
    """
    Right hip external rotation angle.

    :type: int
    :unit: degree
    """

    right_hip_ir = db.Column(db.Integer)
    """
    Right hip internal rotation angle.

    :type: int
    :unit: degree
    """

    right_hip_abd = db.Column(db.Integer)
    """
    Right hip abduction angle.

    :type: int
    :unit: degree
    """

    right_hip_add = db.Column(db.Integer)
    """
    Right hip adduction angle.

    :type: int
    :unit: degree
    """

    right_hip_flexion = db.Column(db.Integer)
    """
    Right hip flexion angle.

    :type: int
    :unit: degree
    """

    right_hip_extension = db.Column(db.Integer)
    """
    Right hip extension angle.

    :type: int
    :unit: degree
    """
