from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to the Users database"""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Class representing a user on the feedback page"""
    __tablename__ = "users"

    username = db.Column(db.Text, primary_key=True, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email= db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, pwd, email, f_name, l_name):
        """Register user w/hashed password & return that user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into readable (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, email=email, first_name=f_name, last_name=l_name)
    

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.
        Return user if valid; else return False."""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False