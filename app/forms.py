
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectMultipleField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember ?')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    FIO = StringField('FIO', validators=[DataRequired()])
    room_number = IntegerField("room number", validators=[DataRequired()])
    photo = FileField('your photo - optional', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    is_organizer = BooleanField('are you organiser ?')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_login(self, login):
        user = User.get_by_login(login)
        if user is not None:
            raise ValidationError('use different name')
        return


class EditProfileForm(FlaskForm):
    FIO = StringField('FIO', validators=[DataRequired()])
    room_number = StringField("room number", validators=[DataRequired()])
    photo = FileField('your photo - optional', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    types = SelectMultipleField('Event Types', coerce=int)
    submit = SubmitField('Save changes')


class CommentForm(FlaskForm):
    message = TextAreaField('comment', validators=[DataRequired()])
    grade = IntegerField('event grade', validators=[DataRequired()])
    submit = SubmitField('Send comment')

    def validate_grade(self, grade):
        if grade.data < 0 or grade.data > 10:
            raise ValidationError('grade must be between 0 and 10')
        return


class EventForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Event description', validators=[DataRequired()])
    photo = FileField('event photo', validators=[FileAllowed(['jpg', 'png', 'jpeg']), DataRequired()])
    types = SelectField('Event Types', coerce=int)
    places = SelectField('Event`s place', coerce=int)
    submit = SubmitField('Create new Event')

