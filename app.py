from flask import Flask, render_template, flash, redirect, render_template, request, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Country, State, City
from forms import SearchVenuesForm, LoginForm, UserAddForm
from .env import API_KEY
print("Did my api key make it?", API_KEY)
CURR_USER_KEY = "curr_user"
BASE_URL = "https://app.ticketmaster.com/discovery/v2/"

app = Flask(__name__)

app.config["SECRET_KEY"] = "oh-so-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///gigbook_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/register', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('register.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        else:
            flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    del session[CURR_USER_KEY]

    flash("You have successfully logged out.", "success")
    return redirect("/login")


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("index.html")


@app.route("/search-venues", methods=["GET", "POST"])
def searchVenues():
    """Displays Venue Search form."""

    form = SearchVenuesForm()
    print("before form validate code line")
    if form.validate_on_submit():
        print("sfter form validate code line")
        country = form.country.data
        state = form.state.data
        city = form.city.data

        response = requests.get(f'{BASE_URL}/venues.json?keyword={city}&apikey=')
        print('country, state, city', country, state, city)
        # flash(f'You have successfully searched for venues in {city.name}, {state.name}, {country.name}.')        
        return redirect("/search-venues")

    else:
        return render_template(
            "search-venues.html", form=form)


######################################################
#                                                    #
# routes for dynamic SelectFields in SearchVenueForm #
#                                                    #
######################################################

@app.route("/country/<country>")
def get_states(country):
    states = State.query.filter_by(country_id=country).order_by("name").all()

    stateArr = [{'id': 0, 'name': ""}]

    for state in states:
        stateObj = {}
        stateObj['id'] = state.id
        stateObj['name'] = state.name
        stateArr.append(stateObj)

    return jsonify({'states' : stateArr})


@app.route("/state/<state>")
def get_cities(state):
    cities = City.query.filter_by(state_id=state).order_by("name").all()

    cityArr = [{'id': 0, 'name': ""}]

    for city in cities:
        cityObj = {}
        cityObj['id'] = city.id
        cityObj['name'] = city.name
        cityArr.append(cityObj)

    return jsonify({'cities' : cityArr})
