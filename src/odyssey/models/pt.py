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

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='PTHistory_clientid_fkey',ondelete="CASCADE"), nullable=False)
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


class Chessboard(db.Model):
    """ Mobility assessment table a.k.a Chessboard

    This table stores the repeated mobility assessment measurements. The measurements
    are indexed by :attr:`clientid` and assessment :attr:`timestamp`. All values in
    this table, with the exception of :attr:`isa_dynamic`, are angles in degrees.
    """

    __tablename__ = 'PTChessboard'
    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    """
    Table index.

    :type: int, primary key, autoincrement
    """

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid',name='chessboard_clientid_fkey',ondelete="CASCADE"), nullable=False)
    """
    Client ID number

    :type: int, foreign key to :attr:`ClientInfo.clientid`
    """

    timestamp = db.Column(db.DateTime)
    """
    Timestamp of the assessment.

    :type: datetime.datetime, primary key
    """

    isa_right = db.Column(db.Boolean)
    """
    Indicates whether or not the ISA is right.

    :type: bool
    """

    isa_left = db.Column(db.Boolean)
    """
    Indicates whether or not the ISA is left.

    :type: bool
    """

    isa_structure = db.Column(db.String(24))
    """
    must be one of the following
    'Inhaled',
    'Exhaled',
    'Asymmetrical Normal',
    'Asymmetrical Atypical'

    :type: str, max length 24
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

    left_hip_slr = db.Column(db.Integer)
    """
    Left hip SLR

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

    right_hip_slr = db.Column(db.Integer)
    """
    Right hip SLR

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

    right_hip_slr = db.Column(db.Integer)
    """
    Right hip SLR

    :type: int
    """

    notes = db.Column(db.Text)
    """
    notes on the assessment

    :type: str
    """

    def get_attributes(self):
        """attributes for setting values from dictionaries. 
           Timestamp and clientid are purposefully left out. They are set individually
        """
        return ['isa_left', 'isa_right', 'isa_dynamic', 'isa_structure',
            'left_shoulder_er', 'left_shoulder_ir', 'left_shoulder_abd', 'left_shoulder_add',
            'left_shoulder_flexion', 'left_shoulder_extension', 'right_shoulder_er', 'right_shoulder_ir',
            'right_shoulder_abd', 'right_shoulder_add', 'right_shoulder_flexion', 'right_shoulder_extension', 
            'left_hip_er', 'left_hip_ir', 'left_hip_abd', 'left_hip_add', 'left_hip_flexion', 'left_hip_extension', 
            'right_hip_er', 'right_hip_ir', 'right_hip_abd', 'right_hip_add', 'right_hip_flexion', 'right_hip_extension']
    
    def to_dict(self):
        """returns all mobility assessment in dictionary form"""
        data = {
            'clientid': self.clientid,
            'timestamp': self.timestamp,
            'isa_left': self.isa_left,
            'isa_right': self.isa_right,
            'isa_dynamic': self.isa_dynamic,
            'isa_structure': self.isa_structure,
            'left_shoulder_er': self.left_shoulder_er,
            'left_shoulder_ir': self.left_shoulder_ir,
            'left_shoulder_abd': self.left_shoulder_abd,
            'left_shoulder_add': self.left_shoulder_add,
            'left_shoulder_flexion': self.left_shoulder_flexion,
            'left_shoulder_extension': self.left_shoulder_extension,
            'right_shoulder_er': self.right_shoulder_er,
            'right_shoulder_ir': self.right_shoulder_ir,
            'right_shoulder_abd': self.right_shoulder_abd,
            'right_shoulder_add': self.right_shoulder_add,
            'right_shoulder_flexion': self.right_shoulder_flexion,
            'right_shoulder_extension': self.right_shoulder_extension,
            'left_hip_er': self.left_hip_er,
            'left_hip_ir': self.left_hip_ir,
            'left_hip_abd': self.left_hip_abd,
            'left_hip_add': self.left_hip_add,
            'left_hip_flexion': self.left_hip_flexion,
            'left_hip_extension': self.left_hip_extension,
            'right_hip_er': self.right_hip_er,
            'right_hip_ir': self.right_hip_ir,
            'right_hip_abd': self.right_hip_abd,
            'right_hip_add': self.right_hip_add,
            'right_hip_flexion': self.right_hip_flexion,
            'right_hip_extension': self.right_hip_extension,
        }
        return data

    def from_dict(self, data):
        """to be used when a new user is created or a user id edited"""
        attributes = self.get_attributes()

        setattr(self, 'timestamp', datetime.utcnow())
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])

    @staticmethod
    def all_chessboard_entries(query, **kwargs):
        resources = query.all()
        
        data = {
            'items': [item.to_dict() for item in resources],
            '_meta': {
                'total_items': len(resources)
                }
            }
        return data, resources

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
