from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


# Todo improve JSON types to facilitate utilisation
def create_json(cafe):
    if type(cafe) == list:
        if not cafe:
            # List is Empty = No search queries found!
            error_json = jsonify(error={
                    "Not Found": "Sorry, no cafes were found at that location",
                }
            )
            return error_json
        else:
            # List is not Empty!
            cafe_json = jsonify(cafe=cafe)
            return cafe_json
    else:
        cafe_json = jsonify(cafe=cafe)
    return cafe_json


def cafe_to_dict(cafe):
    cafe_dict = {
        "id": cafe.id,
        "name": cafe.name,
        "map_url": cafe.map_url,
        "img_url": cafe.img_url,
        "location": cafe.location,
        "seats": cafe.seats,
        "has_toilet": cafe.has_toilet,
        "has_wifi": cafe.has_wifi,
        "has_sockets": cafe.has_sockets,
        "can_take_calls": cafe.can_take_calls,
        "coffee_price": cafe.coffee_price,
    }

    return cafe_dict


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET", "POST"])
def get_random_cafe():
    query_answer = db.session.query(Cafe).all()
    random_cafe = random.choice(query_answer)
    cafe_json = create_json(cafe_to_dict(random_cafe))
    return cafe_json


@app.route("/all", methods=["GET", "POST"])
def get_all_cafes():
    query_answer = db.session.query(Cafe).all()
    cafe_list = []

    for cafe in query_answer:
        cafe_info = cafe_to_dict(cafe)
        cafe_list.append(cafe_info)
    cafe_list_json = create_json(cafe_list)

    return cafe_list_json


@app.route("/search")
def search_cafe():
    location = request.args.get('location')
    query_answer = db.session.query(Cafe).filter(Cafe.location == location).all()
    cafe_list = []
    for cafe in query_answer:
        cafe_info = cafe_to_dict(cafe)
        cafe_list.append(cafe_info)
    cafe_list_json = create_json(cafe_list)

    return cafe_list_json


if __name__ == '__main__':
    app.run(debug=True)
