from odyssey import db

class PTHistory(db.Model):
    """ Physical therapy history table

    This table stores the physical therapy history of a client. The information
    is taken only once, during the initial consult.
    """

    __tablename__ = 'PTHistory'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
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


class MobilityAssessment(db.Model):
    """ Mobility assessment table

    This table stores the repeated mobility assessment measurements. The measurements
    are indexed by :attr:`clientid` and assessment :attr:`timestamp`. All values in
    this table, with the exception of :attr:`isa_dynamic`, are angles in degrees.
    """

    __tablename__ = 'MobilityAssessment'

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'),
                        nullable=False, primary_key=True)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    timestamp = db.Column(db.DateTime, primary_key=True)
    """
    Timestamp of the assessment.

    :type: datetime.datetime, primary key
    """

    isa_left = db.Column(db.Integer)
    """
    ISA? left

    :type: int
    """

    isa_right = db.Column(db.Integer)
    """
    ISA? left

    :type: int
    """

    isa_dynamic = db.Column(db.Boolean)
    """
    Indicates whether or not the ISA is dynamic.

    :type: bool
    """

    left_shoulder_er = db.Column(db.Integer)
    """
    Left shoulder external rotation

    :type: int
    """

    left_shoulder_ir = db.Column(db.Integer)
    """
    Left shoulder internal rotation

    :type: int
    """

    left_shoulder_abd = db.Column(db.Integer)
    """
    Left shoulder abduction.

    :type: int
    """

    left_shoulder_add = db.Column(db.Integer)
    """
    Left shoulder adduction

    :type: int
    """

    left_shoulder_flexion = db.Column(db.Integer)
    """
    Left shoulder flexion.

    :type: int
    """

    left_shoulder_extension = db.Column(db.Integer)
    """
    Left shoulder extension.

    :type: int
    """

    right_shoulder_er = db.Column(db.Integer)
    """
    Right shoulder external rotation

    :type: int
    """

    right_shoulder_ir = db.Column(db.Integer)
    """
    Right shoulder internal rotation

    :type: int
    """

    right_shoulder_abd = db.Column(db.Integer)
    """
    Right shoulder abduction.

    :type: int
    """

    right_shoulder_add = db.Column(db.Integer)
    """
    Right shoulder adduction

    :type: int
    """

    right_shoulder_flexion = db.Column(db.Integer)
    """
    Right shoulder flexion.

    :type: int
    """

    right_shoulder_extension = db.Column(db.Integer)
    """
    Right shoulder extension.

    :type: int
    """

    left_hip_er = db.Column(db.Integer)
    """
    Left hip external rotation

    :type: int
    """

    left_hip_ir = db.Column(db.Integer)
    """
    Left hip internal rotation

    :type: int
    """

    left_hip_abd = db.Column(db.Integer)
    """
    Left hip abduction.

    :type: int
    """

    left_hip_add = db.Column(db.Integer)
    """
    Left hip adduction

    :type: int
    """

    left_hip_flexion = db.Column(db.Integer)
    """
    Left hip flexion.

    :type: int
    """

    left_hip_extension = db.Column(db.Integer)
    """
    Left hip extension.

    :type: int
    """

    right_hip_er = db.Column(db.Integer)
    """
    Right hip external rotation

    :type: int
    """

    right_hip_ir = db.Column(db.Integer)
    """
    Right hip internal rotation

    :type: int
    """

    right_hip_abd = db.Column(db.Integer)
    """
    Right hip abduction.

    :type: int
    """

    right_hip_add = db.Column(db.Integer)
    """
    Right hip adduction

    :type: int
    """

    right_hip_flexion = db.Column(db.Integer)
    """
    Right hip flexion.

    :type: int
    """

    right_hip_extension = db.Column(db.Integer)
    """
    Right hip extension.

    :type: int
    """
