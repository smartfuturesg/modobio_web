from odyssey import db


class MedicalHistory(db.Model):
    
    __tablename__ = 'MedicalHistory'
    
    clientid = db.Column(db.Integer, primary_key=True, autoincrement=True)


db.create_all()
