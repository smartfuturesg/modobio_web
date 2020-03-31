from odyssey import db


class PTHistory(db.Model):
    
    __tablename__ = 'PTHistory'
    
    clientid = db.Column(db.Integer, primary_key=True, autoincrement=True)


db.create_all()
