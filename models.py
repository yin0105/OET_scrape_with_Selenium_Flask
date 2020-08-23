from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, TextAreaField, SelectField, DateField, HiddenField, IntegerField, ValidationError, PasswordField, SelectMultipleField, BooleanField
from wtforms.validators import Length, Email, InputRequired
from wtforms.fields.html5 import DateField
# from wtforms_components import PhoneNumberField

import phonenumbers


profession_list = []
countries_list = []
locations_list = []
dates_list = []
test_date_list = []

# # Form ORM
class UserForm(FlaskForm):    
        name = TextField(' Name :   ', validators=[InputRequired(),Length(max=50)] )
        username = TextField(' User Name :   ', validators=[InputRequired(),Length(max=50)] )
        password = TextField(' Password :   ', validators=[InputRequired(),Length(max=50)] )
        email = TextField(' Email :   ', validators=[Email(), InputRequired(), ])
        phone = TextField(' Phone :   ', validators=[InputRequired()])
        profession = SelectField(' Profession : ', choices = profession_list)
        country = SelectField(' Country : ', choices =  countries_list)           
        # dates = SelectField(' Dates : ', choices = dates_list)
        dates = TextField('Dates : ', validators=[InputRequired()])
        locations_ = SelectField(' Locations : ', choices = locations_list)
        submit = SubmitField(' Submit')
        id = HiddenField(' id')
        defer = BooleanField("    Defer Application")
        test_date = SelectField(' Date of Test : ', choices = test_date_list)


        orig_email = HiddenField("Original Email")

        def validate_phone(self, phone):
                try:
                        p = phonenumbers.parse(phone.data)
                        if not phonenumbers.is_valid_number(p):
                                raise ValueError()
                except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
                        raise ValidationError('Invalid phone number')

class LoginForm(FlaskForm):    
        name = TextField(' Name :   ', validators=[InputRequired(),Length(max=20)] )
        password = PasswordField(' Password :   ', validators=[InputRequired(),Length(max=20)] )
        submit = SubmitField('Log in')  
        

