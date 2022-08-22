from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, Optional, Regexp


class AddUserForm(FlaskForm):
    """Form for adding a new user to the feedback site."""

    username = StringField(
        "Username",
        validators=[
            InputRequired(message="A username is required."),
            Regexp(
                r"^[\w-]+$",
                message="A username must only contain letters, numbers, - , or _",
            ),
        ],
        filters=[lambda str: str.strip() if str else ""],
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
        validators=[
            Length(max=30),
            InputRequired(message="A first name is required."),
            Regexp(
                r"^\S+.*",
                message="First name must contain at least 1 non-space character.",
            ),
        ],
        filters=[lambda str: str.strip() if str else ""],
    )
    last_name = StringField(
        "Last Name",
        validators=[
            Length(max=30),
            InputRequired(message="A last name is required."),
            Regexp(
                r"^\S+.*",
                message="Last name must contain at least 1 non-space character.",
            ),
        ],
        filters=[lambda str: str.strip() if str else ""],
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


class FeedbackForm(FlaskForm):
    """Form to let a user submit feedback to the feedback site."""

    title = StringField(
        "Title",
        validators=[
            Length(max=100),
            InputRequired(message="A title is required."),
            Regexp(
                r"^\S+.*",
                message="Title must contain at least 1 non-space character.",
            ),
        ],
        filters=[lambda str: str.strip() if str else ""],
    )
    content = TextAreaField(
        "Content",
        validators=[
            InputRequired(message="Feedback content is required."),
            Regexp(
                r"^\S+.*",
                message="Content must contain at least 1 non-space character.",
            ),
        ],
        filters=[lambda str: str.strip() if str else ""],
    )


class EditFeedbackForm(FlaskForm):
    """Form to let a user submit feedback to the feedback site."""

    title = StringField(
        "Title",
        validators=[
            Optional(),
            Length(max=100),
            Regexp(
                r"^\S+.*",
                message="Title must contain at least 1 non-space character.",
            ),
        ],
        filters=[lambda str: str.strip() if str else ""],
    )
    content = TextAreaField(
        "Content",
        validators=[
            Optional(),
            Regexp(
                r"^\S+.*",
                message="Content must contain at least 1 non-space character.",
            ),
        ],
        filters=[lambda str: str.strip() if str else ""],
    )
