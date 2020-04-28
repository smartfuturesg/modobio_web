from odyssey import db

class PTHistory(db.Model):

    __tablename__ = 'PTHistory'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)

    exercise = db.Column(db.Text)

    has_pt = db.Column(db.Boolean)
    has_chiro = db.Column(db.Boolean)
    has_massage = db.Column(db.Boolean)
    has_surgery = db.Column(db.Boolean)
    has_medication = db.Column(db.Boolean)
    has_acupuncture = db.Column(db.Boolean)

    pain_areas = db.Column(db.Text)
    best_pain = db.Column(db.Integer)
    worst_pain = db.Column(db.Integer)
    current_pain = db.Column(db.Integer)
    makes_worse = db.Column(db.String(1024))
    makes_better = db.Column(db.String(1024))


class MobilityAssessment(db.Model):

    __tablename__ = 'MobilityAssessment'

    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'),
                        nullable=False, primary_key=True)
    timestamp = db.Column(db.DateTime, primary_key=True)

    isa_left = db.Column(db.Integer)
    isa_right = db.Column(db.Integer)
    isa_dynamic = db.Column(db.Boolean)

    left_shoulder_er = db.Column(db.Integer)
    left_shoulder_ir = db.Column(db.Integer)
    left_shoulder_abd = db.Column(db.Integer)
    left_shoulder_add = db.Column(db.Integer)
    left_shoulder_flexion = db.Column(db.Integer)
    left_shoulder_extension = db.Column(db.Integer)

    right_shoulder_er = db.Column(db.Integer)
    right_shoulder_ir = db.Column(db.Integer)
    right_shoulder_abd = db.Column(db.Integer)
    right_shoulder_add = db.Column(db.Integer)
    right_shoulder_flexion = db.Column(db.Integer)
    right_shoulder_extension = db.Column(db.Integer)

    left_hip_er = db.Column(db.Integer)
    left_hip_ir = db.Column(db.Integer)
    left_hip_abd = db.Column(db.Integer)
    left_hip_add = db.Column(db.Integer)
    left_hip_flexion = db.Column(db.Integer)
    left_hip_extension = db.Column(db.Integer)

    right_hip_er = db.Column(db.Integer)
    right_hip_ir = db.Column(db.Integer)
    right_hip_abd = db.Column(db.Integer)
    right_hip_add = db.Column(db.Integer)
    right_hip_flexion = db.Column(db.Integer)
    right_hip_extension = db.Column(db.Integer)
