import re
from flask import Flask, render_template, flash, redirect, render_template, request, session, g, jsonify
import requests
from flask_debugtoolbar import DebugToolbarExtension
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
# from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

from models import db, connect_db, User, Country, State, City, Favorite
from forms import EditProfileForm, SearchVenuesForm, LoginForm, UserAddForm

from secret import API_KEY

CURR_USER_KEY = "curr_user"
BASE_URL = "https://app.ticketmaster.com/discovery/v2"
DEFAULT_IMG_URL = "/static/images/default-pic.png"

app = Flask(__name__)

app.config["SECRET_KEY"] = "oh-so-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///gigbook_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

######################################
#                                    #
#           Routes Setup             #
#                                    #
######################################

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
    session["favorites"] = []
    for fav in user.favorites:
        session["favorites"].append(fav.venue_name)


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


#########################################
#                                       #
#      Register, Login and Logout       #
#                                       #
#########################################

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
                city=form.city.data,
                state=form.state.data,
                image_url=form.image_url.data or DEFAULT_IMG_URL,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken.", 'danger')
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


#################################
#                               #
#           Home Route          #
#                               #
#################################


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("index.html")


######################################
#                                    #
#            User Routes             #
#                                    #
######################################

@app.route('/users')
def get_all_users():
    """Show all users."""

    users = User.query.all()

    return render_template('all-users.html', users=users)


@app.route("/users/<int:user_id>")
def show_profile(user_id):
    """Shows user profile."""

    user = User.query.get(user_id)
    
    if not user:

            flash("User does not exist.", "danger")
            return redirect('/')
    
    if g.user:
        
        return render_template("user-profile.html", user=user)

    else:

        flash("You must logged in before viewing profile.", "danger")

        return redirect('/login')


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_profile(user_id):
    """Shows edit form for user profile."""

    user = User.query.get(user_id)

    form = EditProfileForm(obj=user)

    if not user:
        flash("User does not exist.", "danger")
        return redirect('/')

    if not g.user:
        flash("You must be logged in to edit profile.", "danger")
        return redirect('/')

    if g.user.id != user.id:
        flash("You are not authorized to edit this profile.", "danger")
        return redirect('/')

    if g.user.id == user.id:

        if form.validate_on_submit():

            
            user.email = form.email.data
            user.image_url = form.image_url.data or None

            user.city = form.city.data
            user.state = form.state.data

            db.session.commit()

            return redirect(f"/users/{ user.id }")

    return render_template("edit-profile.html", form=form, user=user)

        
@app.route('/users/<int:user_id>/delete', methods=["GET", "POST"])
def delete_profile(user_id):
    """Deletes profile of signed in user."""

    user = User.query.get(user_id)

    if not user:
        flash("User does not exist.", "danger")
        return redirect('/')
    
    if not g.user:
        flash("You must be logged in to delete account.", "danger")
        return redirect('/')

    if g.user.id != user.id:
        flash("You are not authorized to delete this account.", "danger")
        return redirect('/')

    if g.user and g.user.id == user.id:
        do_logout()

        db.session.delete(g.user)
        db.session.commit()

        flash("You have successfully deleted your account.", "success")
        return redirect('/')


################################
#                              #
#        Search Venues         #
#                              #
################################


@app.route("/search-venues", methods=["GET", "POST"])
def searchVenues():
    """Displays Venue Search form. On submit, Ticketmaster 
    API is called and response is returned in JSON format, 
    to be displayed on page as list of venues."""
    
    if CURR_USER_KEY in session:

        user = User.query.get(session[CURR_USER_KEY])
        userFavs = [fav.venue_name for fav in user.favorites]
        print("user favs", userFavs)

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
        print(response.json())
        venues = []
        numPages = response.json()["page"]["totalPages"]

        i = 0

        while i < numPages:

            resp = requests.get(f'{BASE_URL}/venues.json?size=200&page={i}&sort=name,asc&keyword={c.name}&apikey={API_KEY}')

            if resp.json()["_embedded"]["venues"]:
                
                for venue in resp.json()["_embedded"]["venues"]:
                    # if venue["address"]["line1"]:
                    #     print(venue["address"]["line1"])   
                    if venue["city"]["name"] == c.name:
                        
                        if venue["state"]:
                            
                            if venue["state"]["name"] == s.name:

                                ven = {
                                    "name": venue["name"], 
                                    # "address": venue["address"]["line1"], 
                                    "city": venue["city"]["name"], 
                                    "postalCode": venue["postalCode"], 
                                    "state": venue["state"]["name"]
                                }

                                venues.append(ven)
                                
                                # else:

                                #     ven = {
                                #         "name": venue["name"], 
                                #         "address": "Address Unknown", 
                                #         "city": venue["city"]["name"], 
                                #         "postalCode": venue["postalCode"], 
                                #         "state": venue["state"]["name"]
                                #     }

                                #     venues.append(ven)

                        
                        else:
                            
                            ven = {
                                        "name": venue["name"], 
                                        # "address": venue["address"]["line1"], 
                                        "city": venue["city"]["name"], 
                                        "postalCode": venue["postalCode"]
                                    }

                            venues.append(ven)

                i += 1

        return render_template('search-venues.html', form=form, venues=venues)

    else:
        return render_template(
            "search-venues.html", form=form)


######################################################
#                                                    #
# Favorites Routes #
#                                                    #
######################################################


@app.route('/favorites/add', methods=["GET", "POST"])
def add_favorite():
    """Creates favorite from venue and adds to favorites table in DB."""

    ven_name = request.json['venue_name']
    favorite = Favorite(user_id=session[CURR_USER_KEY], venue_name=ven_name)

    db.session.add(favorite)
    db.session.commit()

    # return redirect('/search-venues')

    
@app.route('/favorites/<int:venue_id>/delete', methods=["GET", "POST"])
def delete_favorite(venue_id):
    """Removes venue from favorites table."""

    # ven_name = request.json['venue_name']
    favorite = Favorite.query.get(venue_id)

    db.session.delete(favorite)
    db.session.commit()

    return redirect(f'/users/{ session[CURR_USER_KEY] }')

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
