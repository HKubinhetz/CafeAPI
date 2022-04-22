# ---------------------------------- IMPORTS ----------------------------------
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random


# --------------------------------- CONSTANTS ---------------------------------
CAFE_API_KEY = "LoveYouBunnyPig0123"


# --------------------------------- APP CONFIG --------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --------------------------------- CAFE CLASS --------------------------------
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


# --------------------------------- FUNCTIONS ---------------------------------
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


def string_to_bool(string):
    if string == "True" or string == "1":
        return 1
    elif string == "False" or string == "0":
        return 0
    else:
        return "String is not a valid boolean value!"


# ---------------------------------- ROUTING ----------------------------------

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


@app.route("/add", methods=["GET", "POST"])
def add_cafe():

    # TODO - Convert all these to a smaller function
    cafe_name = request.args.get('name')
    cafe_map_url = request.args.get('map_url')
    cafe_img_url = request.args.get('img_url')
    cafe_location = request.args.get('location')
    cafe_seats = request.args.get('seats')
    cafe_has_toilet = string_to_bool(request.args.get('has_toilet'))                # Special Boolean Cases
    cafe_has_wifi = string_to_bool(request.args.get('has_wifi'))
    cafe_has_sockets = string_to_bool(request.args.get('has_sockets'))
    cafe_can_take_calls = string_to_bool(request.args.get('can_take_calls'))
    cafe_coffee_price = request.args.get('coffee_price')

    new_cafe = Cafe(name=cafe_name,
                    map_url=cafe_map_url,
                    img_url=cafe_img_url,
                    location=cafe_location,
                    seats=cafe_seats,
                    has_toilet=cafe_has_toilet,
                    has_wifi=cafe_has_wifi,
                    has_sockets=cafe_has_sockets,
                    can_take_calls=cafe_can_take_calls,
                    coffee_price=cafe_coffee_price
                    )

    db.session.add(new_cafe)
    print(new_cafe)
    db.session.commit()

    # TODO - Add this JSON response to the create_json in an ordely way! maybe create a "method" parameter.
    return jsonify(response={
        "success": "Successfully added a new cafe!",
        }
    )


@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    # Search query by ID then print here.
    print(cafe_id)
    # Fetch the price arguments
    new_price = request.args.get('price')
    print(new_price)

    try:
        # Query the correct Café by its id
        selected_cafe = db.session.query(Cafe).filter(Cafe.id == cafe_id).first()
        print(selected_cafe.name)
        # Update and commit!
        print(selected_cafe.coffee_price)
        selected_cafe.coffee_price = new_price
        print(selected_cafe.coffee_price)
        db.session.commit()
        # TODO -  Query the JSON and print it out!
        # TODO - Add this JSON response to the create_json in an ordely way! maybe create a "method" parameter.
        return jsonify(response={
            "success": "Successfully updated a price for your Cafe!",
            }
        ), 200
    except AttributeError:
        # TODO - Add this JSON response to the create_json in an ordely way! maybe create a "method" parameter.
        return jsonify(error={
            "Not Found": "Sorry! This Cafe was not found.",
        }
        ), 404


@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def close_cafe(cafe_id):
    key_check = True
    # TODO - Implement a query by id here. Create a function.
    # KUBINHA TIP - A NON EXISTING ID WILL RETURN "AttributeError: 'NoneType' object has no attribute 'name'"
    # Use it as a guide!

    selected_cafe = db.session.query(Cafe).filter(Cafe.id == cafe_id).first()
    print(selected_cafe.name)

    # TODO - Implement a API Key check based on the constant. Then enter the decision loop down below

    # Testing the API Key
    api_key = request.args.get('api_key')
    print(f"Your API Key is: {api_key}")

    # TODO - This decision loop can become a function for easier routing readability

    if api_key == CAFE_API_KEY:
        print("This is the correct API KEY")
    else:
        print("You have an invalid API Key")

    if key_check and cafe_id:
        return jsonify(response={
            "success": "Successfully removed a closed Café!",
        }
        ), 200
    elif not cafe_id:
        return jsonify(error={
            "Not Found": "Sorry! This Cafe was not found.",
        }
        ), 404
    elif not key_check:
        return jsonify(error={
            "Not Allowed": "Sorry! You do not have a valid API Key to do this.",
        }
        ), 403


# ---------------------------------- RUNNING ----------------------------------
if __name__ == '__main__':
    app.run(debug=True)
