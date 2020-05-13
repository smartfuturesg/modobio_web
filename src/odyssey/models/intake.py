from odyssey import db

class ClientInfo(db.Model):

    __tablename__ = 'ClientInfo'

    clientid = db.Column(db.Integer, primary_key=True, autoincrement=True)

    firstname = db.Column(db.String(50))
    middlename = db.Column(db.String(50))
    lastname = db.Column(db.String(50))

    # Generated from first + last, should be done in db
    fullname = db.Column(db.String(100))

    guardianname = db.Column(db.String(100))
    guardianrole = db.Column(db.String(50))

    street = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(10))
    country = db.Column(db.String(2))

    # Generated from street + city + state + zip, should be done in db
    address = db.Column(db.String(120))

    email = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    preferred = db.Column(db.SmallInteger)

    ringsize = db.Column(db.Float)

    emergency_contact = db.Column(db.String(50))
    emergency_phone = db.Column(db.String(20))

    healthcare_contact = db.Column(db.String(50))
    healthcare_phone = db.Column(db.String(20))

    gender = db.Column(db.String(1))
    dob = db.Column(db.Date)

    receive_docs = db.Column(db.Boolean)


class ClientConsent(db.Model):

    __tablename__ = 'ClientConsent'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)

    infectious_disease = db.Column(db.Boolean)
    signdate = db.Column(db.Date)
    signature = db.Column(db.Text)


class ClientRelease(db.Model):

    __tablename__ = 'ClientRelease'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)

    release_by_other = db.Column(db.String(1024))
    release_to_other = db.Column(db.String(1024))
    release_of_all = db.Column(db.Boolean)
    release_of_other = db.Column(db.String(1024))
    release_date_from = db.Column(db.Date)
    release_date_to = db.Column(db.Date)
    release_purpose = db.Column(db.String(1024))

    signdate = db.Column(db.Date)
    signature = db.Column(db.Text)


class ClientPolicies(db.Model):

    __tablename__ = 'ClientPolicies'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)

    signdate = db.Column(db.Date)
    signature = db.Column(db.Text)


class ClientConsultContract(db.Model):

    __tablename__ = 'ClientConsultContract'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)

    signdate = db.Column(db.Date)
    signature = db.Column(db.Text)


class ClientSubscriptionContract(db.Model):

    __tablename__ = 'ClientSubscriptionContract'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)

    signdate = db.Column(db.Date)
    signature = db.Column(db.Text)


class ClientIndividualContract(db.Model):

    __tablename__ = 'ClientIndividualContract'

    idx = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientid = db.Column(db.Integer, db.ForeignKey('ClientInfo.clientid'), nullable=False)

    doctor = db.Column(db.Boolean, default=False)
    pt = db.Column(db.Boolean, default=False)
    data = db.Column(db.Boolean, default=False)
    drinks = db.Column(db.Boolean, default=False)

    signdate = db.Column(db.Date)
    signature = db.Column(db.Text)
