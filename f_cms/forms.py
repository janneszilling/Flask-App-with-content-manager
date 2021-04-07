from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from markupsafe import Markup
from f_cms.models import User

class UserRegistrationForm(FlaskForm):
    username = StringField('First and last name', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "John Doe"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "name@email.com"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)], render_kw={"placeholder": "Must be minimum 8 characters."})
    submit = SubmitField('Add user')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()], render_kw={"placeholder": "name@email.com"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "********"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Upload', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"height": "400"})
    title_image = FileField('Title Image', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    image_1 = FileField('Upload Image 1', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    image_2 = FileField('Upload Image 2', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    image_3 = FileField('Upload Image 3', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    image_4 = FileField('Upload Image 4', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    image_5 = FileField('Upload Image 5', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    image_6 = FileField('Upload Image 6', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    submit = SubmitField('Create')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "name@email.com"})
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)], render_kw={"placeholder": "Must be minimum 8 characters."})
    submit = SubmitField('Reset Password')
