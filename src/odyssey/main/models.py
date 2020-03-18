from odyssey import db

class Employees(db.Model):
    __tablename__ = 'Employees'

    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(128))

db.create_all()
