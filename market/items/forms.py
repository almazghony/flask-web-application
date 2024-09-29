from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, RadioField, IntegerField, TextAreaField
from wtforms.validators import Length,  DataRequired, NumberRange



class RemoveForm(FlaskForm):
    submit = SubmitField(label='Remove')


class PostForm(FlaskForm):
    name = StringField(label='Name', validators=[Length(max=30), DataRequired()])
    description = TextAreaField(label='Description', validators=[Length(max=1500), DataRequired()])
    location = StringField(label='Location', validators=[Length(max=200), DataRequired()])
    price = IntegerField(label='Price', validators=[DataRequired(), NumberRange(min=1, message='الرجاء إدخال سعر أكبر من 0.')])
    type = RadioField(label='Category:', choices=[('electronics', 'Electronics'), ('clothes', 'Clothes')], validators=[DataRequired()])
    delivery = RadioField(label='Delivery:', choices=[('Yes', 'Yes'), ('No', 'No')], validators=[DataRequired()])
    picture = FileField('Add Pictures', validators=[FileAllowed(['jpeg', 'png', 'jpg'])])
    submit = SubmitField(label='Post Item')


class UpdateItem(FlaskForm):

    name = StringField(label='Name', validators=[Length(max=30), DataRequired()])
    description = TextAreaField(label='Description', validators=[Length(max=1500), DataRequired()])
    location = StringField(label='Location', validators=[Length(max=200), DataRequired()])
    price = IntegerField(label='Price', validators=[DataRequired(), NumberRange(min=1, message='الرجاء إدخال سعر أكبر من 0.')])
    type = RadioField(label='Category', choices=[('electronics', 'Electronics'), ('clothes', 'Clothes')], validators=[DataRequired()])
    images = FileField('Add Pictures', validators=[FileAllowed(['jpeg', 'png', 'jpg'])])
    submit = SubmitField(label='Post Item')
        
