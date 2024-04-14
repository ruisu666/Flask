from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.utils import get_cursor, hash_password  # Import hash_password function
from flask import session  # Import session object
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()]) 
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UserRegistrationForm(FlaskForm):
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

    def validate_contactnumber(self, contactnumber):
        """
        Custom contact number validation to check if the number can be texted.
        """
        try:
            parsed_number = phonenumbers.parse(contactnumber.data, "PH")
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError('Invalid phone number format. Please enter a valid Philippine phone number.')
        except NumberParseException as e:
            raise ValidationError('Invalid phone number format. Please enter a valid Philippine phone number.')

        if len(contactnumber.data) != 11:
            raise ValidationError('Contact number must be 11 digits long.')
        
    def validate_password(self, password):
        """
        Custom password validator.
        """
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

class AccountRecoveryForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Verification Email')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

    def validate_password(self, password):
        """
        Custom password validator.
        """
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

    def validate_password_change(self, password):
        """
        Custom password change validation to ensure the new password is different from the old one.
        """
        old_password_hash = session.get('old_password_hash')
        new_password_hash = hash_password(password.data) 

        if new_password_hash == old_password_hash:
            raise ValidationError('New password must be different from the old one.')

class AdminRegistrationForm(FlaskForm):
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    confirm_email = StringField('Confirm Email', validators=[DataRequired(), Email(), EqualTo('email', message='Emails must match')])
    contactnumber = StringField('Contact Number', validators=[DataRequired(), Length(min=11, max=11)])
    confirm_contactnumber = StringField('Confirm Contact Number', validators=[DataRequired(), EqualTo('contactnumber', message='Contact numbers must match')])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Submit')

    def validate_contactnumber(self, contactnumber):
        """
        Custom contact number validation to check if the number can be texted.
        """
        try:
            parsed_number = phonenumbers.parse(contactnumber.data, "PH")
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError('Invalid phone number format. Please enter a valid Philippine phone number.')
        except NumberParseException as e:
            raise ValidationError('Invalid phone number format. Please enter a valid Philippine phone number.')

        if len(contactnumber.data) != 11:
            raise ValidationError('Contact number must be 11 digits long.')
        
    def validate_password(self, password):
        """
        Custom password validator.
        """
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

    def validate_email(self, email):
        """
        Custom email validation to check for uniqueness.
        """
        cursor, connection = get_cursor() 
        query = "SELECT COUNT(*) FROM admin WHERE email = %s"
        cursor.execute(query, (email.data,))
        result = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        if result > 0:
            raise ValidationError('Email address is already in use. Please use a different email.')

class AddVehicleForm(FlaskForm):
    model = StringField('Model', validators=[DataRequired()])
    license_plate = StringField('License Plate', validators=[DataRequired()])
    submit = SubmitField('Submit')
        
