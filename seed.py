from app import app
from models import User, Country, State, City, db, connect_db

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///gigbook_db"

connect_db(app)

db.drop_all()
db.create_all()

u = User.signup(username="YogiBoi11", password="password", image_url="")
c = Country(name="United States")

db.session.add_all([u, c])
db.session.commit()

s1 = State(name="Texas", country_id=c.id)
s2 = State(name="California", country_id=c.id)

db.session.add_all([s1, s2])
db.session.commit()

city1 = City(name="Dallas", state_id=s1.id)
city2 = City(name="San Francisco", state_id=s2.id)

db.session.add_all([city1, city2])
db.session.commit()