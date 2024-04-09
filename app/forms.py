from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.utils import get_cursor

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()]) 
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    studno = StringField('Student Number', validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    emailaddress = StringField('Email Address', validators=[DataRequired(), Email()])
    confirm_email = StringField('Confirm Email Address', validators=[DataRequired(), Email(), EqualTo('emailaddress')])
    contactnumber = StringField('Contact Number', validators=[DataRequired(), Length(min=11, max=11)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    vehicle_model = StringField('Vehicle Model', validators=[DataRequired()])
    license_number = StringField('License Number', validators=[DataRequired()])
    submit = SubmitField('Submit')

    # Custom validator for contact number
    def validate_contactnumber(form, field):
        if not field.data.isdigit():
            raise ValidationError('Contact number must contain only numeric characters.')
    
    def validate_password(self, password):
        """
        Custom password validator.
        """
        print(password.data)
        special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?/~"
        if len(password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not any(char.isdigit() for char in password.data):
            raise ValidationError('Password must contain at least one digit.')
        if not any(char.isupper() for char in password.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in password.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not any(char in special_characters for char in password.data):
            raise ValidationError('Password must contain at least one special character.')

    def validate_emailaddress(self, emailaddress):
        """
        Custom email validation to check for uniqueness.
        """
        cursor, connection = get_cursor() 
        query = "SELECT COUNT(*) FROM userinfo WHERE email = %s"
        cursor.execute(query, (emailaddress.data,))
        result = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        if result > 0:
            raise ValidationError('Email address is already in use. Please use a different email.')
