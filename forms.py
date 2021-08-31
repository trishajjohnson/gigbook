"""Form to search venues."""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Optional, Email, DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from models import db, Country, State

# countries = [(country.id, country.name) for country in models.Country.query.all()]

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class EditProfileForm(FlaskForm):
    """Edit Profile Form."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = TextAreaField('(Optional) Bio')
    password = PasswordField('Password', validators=[Length(min=6)])


class SearchVenuesForm(FlaskForm):
    """Form for searching venues."""

    # country = SelectField('Country', choices=countries, allow_blank=True)
    # country = QuerySelectField('Country', query_factory=countries, allow_blank=True, get_label='name')
    # country = QuerySelectField('Country', query_factory=lambda: models.Country.query, allow_blank=True, get_label='name')
    # country = QuerySelectField(label='Country', query_factory=lambda: db.session.query(Country), allow_blank=True, get_label='name')
    state = SelectField(label="State", choices=[(1, "Texas")])
    city = SelectField(label="City", choices=[(1, "Dallas")])


