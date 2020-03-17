from odyssey.intake import db


class ClientInfo(db.Model):
    
    __tablename__ = 'ClientInfo'
    
    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)

    firstname = db.Column(db.String(50))
    middlename = db.Column(db.String(50))
    lastname = db.Column(db.String(50))

    street = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(10))
    country = db.Column(db.String(2))

    email = db.Column(db.String(2))
    phone = db.Column(db.String(20))

    gender = db.Column(db.String(1))
    dob = db.Column(db.Date)


# Where should this go?
db.create_all()
