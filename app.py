from flask import Flask, render_template, flash, redirect, render_template, request, session, g, jsonify
import requests
from flask_debugtoolbar import DebugToolbarExtension
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
# from flask_wtf.csrf import CSRFProtect

from models import db, connect_db, User, Country, State, City
from forms import SearchVenuesForm, LoginForm, UserAddForm

from secret import API_KEY

CURR_USER_KEY = "curr_user"
BASE_URL = "https://app.ticketmaster.com/discovery/v2"

app = Flask(__name__)
# csrf = CSRFProtect(app)
# csrf.init_app(app)

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
    """Displays Venue Search form. On submit, Ticketmaster 
    API is called and response is returned in JSON format, 
    to be displayed on page as list of venues."""
    print("before form is instantiated")
    
    form = SearchVenuesForm()

    if form.validate_on_submit():
        state = int(form.state.data)
        city = int(form.city.data)
        
        s = State.query.get(state)
        c = City.query.get(city)

        # example of sending request with a limit on number of venues returned 

        # response = requests.get(f'{BASE_URL}/venues.json?size=5&keyword={c.name}&apikey={API_KEY}')

        # returns venues with no limit 

        response = requests.get(f'{BASE_URL}/venues.json?size=200&sort=name,asc&keyword={c.name}&apikey={API_KEY}')
        
        venues = []
        numPages = response.json()["page"]["totalPages"]

        i = 0

        while i <= numPages:

            resp = requests.get(f'{BASE_URL}/venues.json?size=200&page={i}&sort=name,asc&keyword={c.name}&apikey={API_KEY}')

            for venue in resp.json()["_embedded"]["venues"]:
                
                if venue["city"]["name"] == c.name and venue["state"]:
                    ven = {"name": venue["name"], "city": venue["city"]["name"], "state": venue["state"]["name"]}
                    venues.append(ven)
                    
                else:
                    ven = {"name": venue["name"], "city": venue["city"]["name"]}
                    venues.append(ven)

            i += 1
            
        return render_template('search-venues.html', form=form, venues=venues)

    else:
        return render_template(
            "search-venues.html", form=form)


@app.route("/users/<int:user_id>")
def show_profile(user_id):
    """Shows user profile."""

    user = User.query.get(user_id)

    if g.user and user.id == g.user.id:

        return render_template("user-profile.html", user=user)

    else:

        flash("You must login before viewing profile.")

        return render_template("login.html")
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
