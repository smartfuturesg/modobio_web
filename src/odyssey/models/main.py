from odyssey import db

class Staff(db.Model):
    __tablename__ = 'Staff'

    staffid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    fullname = db.Column(db.String(50))
    password = db.Column(db.String(128))
