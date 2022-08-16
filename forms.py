from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Email, Length


class AddUserForm(FlaskForm):
    """Form for adding a new user to the feedback site."""

    username = StringField(
        "Username", validators=[InputRequired(message="A username is required.")]
    )
    password = PasswordField(
        "Password", validators=[InputRequired(message="A password is required.")]
    )
    email = EmailField(
        "Email",
        validators=[
            Email(message="That is not a valid email"),
            Length(max=50),
            InputRequired(message="An email is required."),
        ],
    )
    first_name = StringField(
        "First Name",
        validators=[Length(max=30), InputRequired(message="A first name is required.")],
    )
    last_name = StringField(
        "Last Name",
        validators=[Length(max=30), InputRequired(message="A last name is required.")],
    )


class LoginForm(FlaskForm):
    """Form to let a returning user sign in to the feedback site."""

    username = StringField(
        "Username",
        validators=[InputRequired(message="A username is required to sign in.")],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(message="A password is required to sign in.")],
    )
