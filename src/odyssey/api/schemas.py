from datetime import datetime
from hashlib import md5

from marshmallow import Schema, fields, post_load, ValidationError, validates, validate
from marshmallow import post_load, post_dump

from odyssey import ma
from odyssey.models.intake import ClientInfo, RemoteRegistration

class ClientInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClientInfo

    @post_load
    def make_object(self, data, **kwargs):
        return ClientInfo(**data)

    @post_dump
    def add_record_locator_id(self,data, **kwargs ):
        name_hash = md5(bytes((data['firstname']+data['lastname']), 'utf-8')).hexdigest()
        data['record_locator_id'] = (data['firstname'][0]+data['lastname'][0]+str(data['clientid'])+name_hash[0:6]).upper()
        return data

class NewRemoteRegistrationSchema(Schema):

    email = fields.Email()
    firstname = fields.String(required=True, validate=validate.Length(min=1, max= 50))
    lastname = fields.String(required=True, validate=validate.Length(min=1,max=50))
    middlename = fields.String(required=False, validate=validate.Length(min=1,max=50))

    @post_load
    def make_object(self, data, **kwargs):
        return ClientInfo(**data)

class ClientRemoteRegistrationSchema(ma.SQLAlchemyAutoSchema):
    """
        holds client's access information for remote registration
    """
    class Meta:
        model = RemoteRegistration



    
"""

class Person:
    def __init__(self, name, age, email):
        self.name = name 
        self.age = age
        self.email = email

    def __repr__(self):
        return f'{ self.name } is { self.age } years old.'


class PersonSchema(Schema):
    name = fields.String(validate=validate.Length(max=5))
    age = fields.Integer()
    email = fields.Email()
    location = fields.String(required=False)

    @validates('age')
    def validate_age(self, age):
        if age > 200:
            raise ValidationError('The age is too old!')

    @post_load
    def create_person(self, data, **kwargs):
        return Person(**data)

input_data = {}

input_data['name'] = input('What is your name? ')
input_data['age'] = input('What is your age? ')
input_data['email'] = input('What is your email? ')

try:
    schema = PersonSchema()
    person = schema.load(input_data)

    #person = Person(name=input_data['name'], age=input_data['age'])

    #print(person)

    result = schema.dump(person)

    print(result)
except ValidationError as err:
    print(err)
    print(err.valid_data)
"""