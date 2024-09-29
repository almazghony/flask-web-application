
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, EmailField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from market.models import User
from flask_login import current_user





class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        if User.query.filter_by(username=username_to_check.data).first():
            raise ValidationError('Username already exists!')
        
    def validate_email_address(self, email_address_to_check):
        if User.query.filter_by(email_address=email_address_to_check.data).first():
            raise ValidationError('Emamil Address already exists!')

    name = StringField(label='Name:', validators=[Length(min=2, max=30),DataRequired()])
    email_address = EmailField(label='Email Address:', validators=[Length(max=64), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=8, max=16), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    mobile_number1 = StringField(label='موبايل', validators=[ DataRequired()])
    mobile_number2 = StringField(label='موبايل 2 (اختيارى)')
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    email_address = EmailField(label='Email', validators=[Length(max=64), DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=8, max=64), DataRequired()])
    submit = SubmitField(label='login')


class PurchaseForm(FlaskForm):
    submit = SubmitField(label='Purchase Item')


class RemoveForm(FlaskForm):
    submit = SubmitField(label='Remove')




class UpdateForm(FlaskForm):

    name = StringField(label='Name:', validators=[Length(min=2, max=30),DataRequired()])
    email_address = EmailField(label='Email Address:', validators=[Length(max=64), DataRequired()])
    mobile_number1 = StringField(label='موبايل', validators=[DataRequired()])
    mobile_number2 = StringField(label='موبايل 2 (اختيارى)',  validators=[])
    state = TextAreaField(label='الحالة (اختيارى)',  validators=[Length(max=200)])
    submit = SubmitField(label='تحديث البيانات')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpeg', 'png', 'jpg'])])


    def validate_email_address(self, email_address_to_check):
        if email_address_to_check.data != current_user.email_address:
            if User.query.filter_by(email_address=email_address_to_check.data).first():
                raise ValidationError('Email Address already exists!')
        
    def validate_mobile_number1(self, mobile_number1_to_check):
        if mobile_number1_to_check.data != current_user.mobile_number1:
            if User.query.filter_by(email_address=mobile_number1_to_check.data).first():
                raise ValidationError('Email Address already exists!')

    def validate_mobile_number2(self, mobile_number2_to_check):
        if mobile_number2_to_check.data != current_user.mobile_number2:
            if User.query.filter_by(email_address=mobile_number2_to_check.data).first():
                raise ValidationError('Email Address already exists!')
            

class ResetForm(FlaskForm):
    email_address = StringField('Email', validators=[Length(64), DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[Length(min=8, max=16), DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=8, max=16), DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')



class ResetForm(FlaskForm):
    email_address = StringField('Email', validators=[Length(64), DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[Length(min=8, max=16), DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=8, max=16), DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')