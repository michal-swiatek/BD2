from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surame', validators=[DataRequired(), Length(min=2, max=20)])
    login = StringField('Login', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])

    role = RadioField('Role', choices=[('w', 'Worker'), ('m', 'Manager'), ('a', 'Administrator')])
    department = IntegerField('Department id', validators=[NumberRange(0, 10)])

    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Login')
