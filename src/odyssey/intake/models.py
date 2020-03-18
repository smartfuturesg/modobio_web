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

    gender = db.Column(db.String(1))
    dob = db.Column(db.Date)

    email = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    # Should be an Enum
    preferred = db.Column(db.SmallInteger)

    emergency_contact = db.Column(db.String(50))
    emergency_phone = db.Column(db.String(20))

    healthcare_contact = db.Column(db.String(50))
    healthcare_phone = db.Column(db.String(20))


class HealthcareConsent(db.Model):
    
    __tablename__ = 'HealthcareConsent'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('ClientInfo.userid'), nullable=False)

    infectious_disease = db.Column(db.Boolean)
    fullname = db.Column(db.String(50))
    signature = db.Column(db.String(50))
    signdate = db.Column(db.Date)


# Where should this go?
db.create_all()
