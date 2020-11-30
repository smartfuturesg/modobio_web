from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField


class StaffLoginForm(FlaskForm):
    email = StringField('Email', render_kw={'type': 'email'})
    password = PasswordField('Password')


class ClientSearchForm(FlaskForm):
    firstname = StringField('First name')
    lastname = StringField('Last name')
    email = StringField('Email address', render_kw={'type': 'email'})
    phone = StringField('Phone number', render_kw={'type': 'phone'})
