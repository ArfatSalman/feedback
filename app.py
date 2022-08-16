from sqlite3 import IntegrityError
from flask import Flask, render_template, redirect, session, flash
from models import User, db, connect_db
from forms import AddUserForm, LoginForm
from sqlalchemy import exc
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_default")
uri = os.getenv("DATABASE_URL", "postgresql:///feedback_site")
if uri.startswith("postgres://"):  # since heroku uses 'postgres', not 'postgresql'
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.debug = True

connect_db(app)


@app.before_first_request
def seed_table():
    """Creates intial table of users and feedback to simplify testing the site."""
    db.drop_all()
    db.create_all()
    test_user = User.register(username="test", password="test_pass", email="test_email@email.com", first_name="test_f", last_name="test_l")
    db.session.add(test_user)
    db.session.commit()


# GET /
# Redirect to /register.
@app.route("/")
def display_home():
    """Displays feedback site's homepage."""
    return render_template("index.html")


# GET /register
# Show a form that when submitted will register/create a user. This form should accept a username, password, email, first_name, and last_name.
# Make sure you are using WTForms and that your password input hides the characters that the user is typing!
@app.route("/register")
def display_add_user_form():
    """Displays a form to let a user register a new account."""
    form = AddUserForm()
    return render_template("register.html", form=form)


# POST /register
# Process the registration form by adding a new user. Then redirect to /users/username
@app.route("/register", methods=["POST"])
def add_user():
    """Validates the submitted user and adds them to the database if successful.
    Otherwise, returns to the registration page with error messages visible."""
    form = AddUserForm()
    if form.validate_on_submit():
        user_inputs = form.data
        user_inputs.pop("csrf_token", None)
        added_user = User.register(**user_inputs)
        db.session.add(added_user)
        try:
            db.session.commit()
            session["user"] = added_user.username
            return redirect(f"/users/{added_user.username}")
        except exc.IntegrityError:
            db.session.rollback()
            form.username.errors.append("That username is taken. Please try again.")
            return render_template("register.html", form=form)
    else:
        return render_template("register.html", form=form)

# GET /login
# Show a form that when submitted will login a user. This form should accept a username and a password.
# Make sure you are using WTForms and that your password input hides the characters that the user is typing!
@app.route("/login")
def display_login_form():
    """Displays a form to let a user log in to their account."""
    form = LoginForm()
    return render_template("login.html", form=form)

# POST /login
# Process the login form, ensuring the user is authenticated and going to /users/username if so.
@app.route("/login", methods=["POST"])
def login_user():
    """Authenticates the user's login and displays their details page if successful.
    Otherwise, returns to the login page with error messages visible."""
    form = LoginForm()
    if form.validate_on_submit():
        user_inputs = form.data
        user_inputs.pop("csrf_token", None)
        login_user = User.authenticate(**user_inputs)
        if login_user:
            session["user"] = login_user.username
            return redirect(f"/users/{login_user.username}")
        else:
            form.password.errors.append("That username or password was incorrect. Please try again.")
            return render_template("login.html", form=form)           
    else:
        return render_template("login.html", form=form)

# GET /users/<username>
# Display a template the shows information about that user (everything except for their password)
# You should ensure that only logged in users can access this page.
@app.route("/users/<username>")
def display_user_details(username):
    """Displays a user's account details if they are logged in."""
    current_user = session.get("user", None)
    if current_user and current_user == username:
        user = User.query.filter_by(username=username).first()
        return render_template("user_details.html", user=user)
    else:
        flash("A user's details can only be viewed by that user while they are logged in.", "error")
        return render_template("index.html")

@app.route("/logout")
def logout_user():
    """Logs a user out of the feedback site."""
    session.pop("user", None)
    return redirect("/")
    