
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, ValidationError, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember ?')
    submit = SubmitField('Register')


class RegistrationForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    FIO = StringField('FIO', validators=[DataRequired()])
    room_number = StringField("room number", validators=[DataRequired()])
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

    def validate_room_number(self, room_number):
        try:
            n = int(room_number)
        except:
            raise ValidationError('room number must be an integer')
        else:
            return


class EditProfileForm(FlaskForm):
    FIO = StringField('FIO', validators=[DataRequired()])
    room_number = StringField("room number", validators=[DataRequired()])
    photo = FileField('your photo - optional', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Register')

