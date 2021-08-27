"""SQLAlchemy models for GigBOOK."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"


    @classmethod
    def signup(cls, username, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Country(db.Model):
    """Country in the system."""

    __tablename__ = 'countries'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    states = db.relationship('State')

    # def __repr__(self):
    #     return '{f"<Country #{self.id}: {self.name}>"}'
    
    def __repr__(self):
        return '{}'.format(self.name)


class State(db.Model):
    """State in the system."""

    __tablename__ = 'states'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    country_id = db.Column(
        db.Integer,
        db.ForeignKey('countries.id', ondelete='cascade')
    )

    cities = db.relationship('City')

    def __repr__(self):
        return f"<State #{self.id}: {self.name}>"


class City(db.Model):
    """State in the system."""

    __tablename__ = 'cities'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    state_id = db.Column(
        db.Integer,
        db.ForeignKey('states.id', ondelete='cascade'),
        unique=True
    )     

    def __repr__(self):
        return f"<City #{self.id}: {self.name}>"

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)