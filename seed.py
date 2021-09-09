import os

from app import app
from models import User, Country, State, City, Favorite, db, connect_db

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('POSTGRES_DATABASE_URL', 'postgres:///gigbook_db')

connect_db(app)

db.drop_all()
db.create_all()

u = User.signup(username="YogiBoi11", email="yogiboi11@gmail.com", password="password", city="Dallas", state="Texas", image_url="")
c = Country(name="United States", country_code="US")

db.session.add_all([u, c])
db.session.commit()

s1 = State(name="Texas", state_code="TX", country_id=c.id)

db.session.add(s1)
db.session.commit()

city1 = City(name="Dallas", state_id=s1.id)

db.session.add(city1)
db.session.commit()

fav = Favorite(venue_name="Trees", user_id=1)

db.session.add(fav)
db.session.commit()