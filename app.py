from flask import Flask, render_template, redirect, session, flash
from models import User, Feedback, db, connect_db
from forms import AddUserForm, LoginForm, FeedbackForm, EditFeedbackForm
from sqlalchemy import exc
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
uri = os.getenv("DATABASE_URL")
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
    test_user = User.register(
        username="test",
        password="test_pass",
        email="test_email@email.com",
        first_name="test_f",
        last_name="test_l",
    )
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
        except exc.IntegrityError as error:
            db.session.rollback()
            if 'Key (username)' in error.orig.pgerror:
                form.username.errors.append("That username is already taken.")
            if 'Key (email)' in error.orig.pgerror: 
                form.email.errors.append("That email is already registered.")
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
            form.password.errors.append(
                "That username or password was incorrect. Please try again."
            )
            return render_template("login.html", form=form)
    else:
        return render_template("login.html", form=form)


# GET /users/<username>
# Display a template the shows information about that user (everything except for their password)
# You should ensure that only logged in users can access this page.
# Show all of the feedback that the user has given.
# For each piece of feedback, display with a link to a form to edit
# the feedback and a button to delete the feedback.
# Have a link that sends you to a form to add more feedback and a button to
# delete the user.
# Make sure that only the user who is logged in can successfully view this page.
@app.route("/users/<username>")
def display_user_details(username):
    """Displays a user's account details if they are logged in."""
    current_user = session.get("user", None)
    if current_user and current_user == username:
        user = User.query.get_or_404(username)
        feedback = Feedback.query.filter(Feedback.username == username).order_by(Feedback.id.asc())
        return render_template("user_details.html", user=user, feedback=feedback)
    else:
        flash(
            "A user's details can only be viewed by that user while they are logged in.",
            "error",
        )
        return redirect("/")


# POST /users/<username>/delete
# Remove the user from the database and make sure to also delete all of their feedback.
# Clear any user information in the session and redirect to /.
# Make sure that only the user who is logged in can successfully delete their account.
@app.route("/users/<username>/delete", methods=["POST"])
def delete_feedback(username):
    """Deletes a logged-in user's account and all of their feedback."""
    current_username = session.get("user", None)
    targeted_user = User.query.get_or_404(username)
    if current_username and current_username == targeted_user.username:
        db.session.delete(targeted_user)
        db.session.commit()
        session.pop("user", None)
    else:
        flash(
            "You can only delete your own account and you must be logged in.", "error"
        )
    return redirect("/")


# GET /users/<username>/feedback/add
# Display a form to add feedback.
# Make sure that only the user who is logged in can see this form.
@app.route("/users/<username>/feedback/add")
def display_feedback_form(username):
    """Displays a form to let a logged-in user add feedback to the site."""
    current_username = session.get("user", None)
    if current_username and current_username == username:
        user = User.query.get_or_404(username)
        form = FeedbackForm()
        return render_template("feedback.html", form=form, username=username)
    else:
        flash(
            "A user's feedback form can only be viewed by that user while they are logged in.",
            "error",
        )
        return redirect("/")


# POST /users/<username>/feedback/add
# Add a new piece of feedback and redirect to /users/<username>.
# Make sure that only the user who is logged in can successfully add feedback.
@app.route("/users/<username>/feedback/add", methods=["POST"])
def add_feedback(username):
    """Adds a logged-in user's feedback to the database."""
    current_username = session.get("user", None)
    if current_username and current_username == username:
        user = User.query.get_or_404(username)
        form = FeedbackForm()
        if form.validate_on_submit():
            user_inputs = form.data
            user_inputs.pop("csrf_token", None)
            feedback = Feedback(**user_inputs, username=current_username)
            db.session.add(feedback)
            db.session.commit()
            return redirect(f"/users/{username}#user-feedback")
        else:
            return render_template("feedback.html", form=form)
    else:
        flash("You can only submit feedback while you are logged in.", "error")
        return redirect("/")


# GET /feedback/<feedback-id>/update
# Display a form to edit feedback.
# **Make sure that only the user who has written that feedback can see this form **
@app.route("/feedback/<int:feedback_id>/update")
def display_edit_feedback_form(feedback_id):
    """Displays a form to let a logged-in user edit their feedback."""
    current_username = session.get("user", None)
    targeted_feedback = Feedback.query.get_or_404(feedback_id)
    if current_username and current_username == targeted_feedback.username:
        user = User.query.get_or_404(current_username)
        form = EditFeedbackForm()
        return render_template("feedback_edit.html", form=form, feedback=targeted_feedback)
    else:
        flash("You can only edit your own feedback and you must be logged in.", "error")
        return redirect("/")


# POST /feedback/<feedback-id>/update
# Update a specific piece of feedback and redirect to /users/<username>.
# Make sure that only the user who has written that feedback can update it.
@app.route("/feedback/<int:feedback_id>/update", methods=["POST"])
def edit_feedback(feedback_id):
    """Edits a logged-in user's previously submitted feedback."""
    current_username = session.get("user", None)
    targeted_feedback = Feedback.query.get_or_404(feedback_id)
    if current_username and current_username == targeted_feedback.username:
        user = User.query.get_or_404(current_username)
        form = EditFeedbackForm()
        if form.validate_on_submit():
            user_inputs = form.data
            if user_inputs.get("title") != "":
                targeted_feedback.title = user_inputs.get("title")
            if user_inputs.get("content") != "":
                targeted_feedback.content = user_inputs.get("content")
            db.session.add(targeted_feedback)
            db.session.commit()
            return redirect(f"/users/{current_username}#user-feedback")
        else:
            return render_template("feedback_edit.html", form=form)
    else:
        flash("You can only edit your own feedback and you must be logged in.", "error")
        return redirect("/")


# POST /feedback/<feedback-id>/delete
# Delete a specific piece of feedback and redirect to /users/<username>
# Make sure that only the user who has written that feedback can delete it.
@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_user(feedback_id):
    """Deletes a logged-in user's previously submitted feedback."""
    current_username = session.get("user", None)
    targeted_feedback = Feedback.query.get_or_404(feedback_id)
    if current_username and current_username == targeted_feedback.username:
        user = User.query.get_or_404(current_username)
        db.session.delete(targeted_feedback)
        db.session.commit()
        return redirect(f"/users/{current_username}#user-feedback")
    else:
        flash(
            "You can only delete your own feedback and you must be logged in.", "error"
        )
        return redirect("/")


@app.route("/logout")
def logout_user():
    """Logs a user out of the feedback site."""
    session.pop("user", None)
    return redirect("/")

@app.errorhandler(404)
def display_404_page(error):
    """Displays the 404 page if a 404 error occurs."""
    return render_template("404.html")
