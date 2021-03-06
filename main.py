# ---------------------------------- IMPORTS ----------------------------------
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import random


# --------------------------------- CONSTANTS ---------------------------------
CAFE_API_KEY = "LoveYouBunnyPig0123"                             # An example API Key


# --------------------------------- APP CONFIG --------------------------------
app = Flask(__name__)                                           # Creating Flask Server
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'    # Connecting Server to DB directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False            # Disabling non-essentials
db = SQLAlchemy(app)                                            # Creating DB App


# --------------------------------- CAFE CLASS --------------------------------
class Cafe(db.Model):
    # The cafe class is exactly what the Database consists of. This structure
    # will be used for every CRUD (Create, Read, Update Delete) operation down the line.

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
def create_cafe_json(json_model, message):
    # This function formats the Cafe JSONS.
    # It returns data from one or several Cafes if valid data is received.
    # If no Cafes are provided, it returns an error message.

    # HTTP Response Codes used in this function:
    # 200 = OK
    # 400 = Bad Request
    # 404 = Not Found

    if json_model == "Several":
        # "Several" = More than one Cafe in the list.
        if not message:
            # In python, "List is Empty" = False
            # This means that no search queries were found!
            error_json = jsonify(error={"Not Found": "Sorry, no cafes were found at that location"})
            return error_json, 404
        else:
            # Else = there are elements in the list! So "List not Empty" = True
            cafe_json = jsonify(cafes=message)
            return cafe_json, 200

    elif json_model == "Single":
        # "Single" = A single Caf?? in the list!
        cafe_json = jsonify(cafe=message)
        return cafe_json, 200

    else:
        # No "Single" nor "Several" caf?? model provided.
        # It raises an error JSON.
        return jsonify(error={"Bad Request": "Sorry! An invalid request has been made."}), 400


def cafe_to_dict(cafe):
    # A simple data manipulation function.
    # It converts cafe info into a dictionary.
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
    # This function is a data conversion tool.
    # It returns a 1 or 0 integer when it receives a
    # 'True'/'1' or a 'False'/'0', respectively.

    # It is used in the Add Caf?? request, as the boolean
    # entries must to be converted to the database's format.

    if string == "True" or string == "1":
        return 1
    elif string == "False" or string == "0":
        return 0
    else:
        return "String is not a valid boolean value!"


def api_key_check(api_key):
    # This function checks the validity of
    # the provided API Key.

    if api_key == CAFE_API_KEY:
        print("This is the correct API KEY")
        return True
    else:
        print("You have an invalid API Key")
        return False


def cafe_check(cafe_id):
    # This function checks the validity of
    # the provided cafe.
    if cafe_id:
        return True
    else:
        return False


def confirm_delete(api_check, cafe_id_check):
    # This function receives the API Key and Valid Cafe checks.
    # Then, it decides if a cafe should be deleted and acts accordingly.

    if api_check and cafe_id_check:
        # All's good. Return a True flag (Good to Delete), a JSON and a 'OK' HTML Response Code
        return True, jsonify(response={"success": "Successfully removed a closed Caf??!"}), 200

    elif not cafe_id_check:
        # Invalid Cafe. Return a False flag (Not to Delete), a JSON and a 'Not Found' HTML Response Code
        return False, jsonify(error={"Not Found": "Sorry! This Cafe was not found."}), 404

    elif not api_check:
        # Invalid API Key. Return a False flag (Not to Delete), a JSON and a 'Forbidden' HTML Response Code
        return False, jsonify(error={"Not Allowed": "Sorry! You do not have a valid API Key to do this."}), 403


# ---------------------------------- ROUTING ----------------------------------
@app.route("/")
def home():
    # Default routing, renders a simple template.
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    # "Random Cafe" routing, queries the DB for a random Cafe.
    # It fetches all data from the database, then randomly
    # chooses one row through python's random library.

    query_answer = db.session.query(Cafe).all()         # Querying all Cafes
    random_cafe = random.choice(query_answer)           # Randomly choosing one of them

    # Creating and returning a Cafe JSON through a function
    cafe_json, response_code = create_cafe_json(json_model="Single", message=cafe_to_dict(random_cafe))
    return cafe_json, response_code


@app.route("/all")
def get_all_cafes():
    # "All Cafes" routing, queries the DB for all data,
    # then formats the rows into a JSON and returns it
    # to the requesting entity.

    query_answer = db.session.query(Cafe).all()         # Querying all Cafes
    cafe_list = []                                      # Creating an empty list to be populated with Cafes

    for cafe in query_answer:
        # For every Cafe on the database, convert it into a dictionary and add into the list.
        cafe_info = cafe_to_dict(cafe)
        cafe_list.append(cafe_info)

    # Converting the list into a JSON and finally returning it to the requesting entity.
    cafe_list_json, response_code = create_cafe_json(json_model="Several", message=cafe_list)
    return cafe_list_json, response_code


@app.route("/search")
def search_cafe():
    # "Search Cafe" routing, very similar to the "All Cafes" routing.
    # Queries the DB for all data, but filters it based on provided "location".
    # The function then formats the rows into a JSON and returns it
    # to the requesting entity.

    location = request.args.get('location')                                             # Request search parameters.
    query_answer = db.session.query(Cafe).filter(Cafe.location == location).all()       # Filtering the query.
    cafe_list = []                                                                      # Empty List to be populated

    for cafe in query_answer:
        # For every Cafe on the database, convert it into a dictionary and add into the list.
        cafe_info = cafe_to_dict(cafe)
        cafe_list.append(cafe_info)

    # Converting the list into a JSON and finally returning it to the requesting entity.
    cafe_list_json = create_cafe_json(json_model="Several", message=cafe_list)
    return cafe_list_json


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    # "Add Cafe" routing. It receives several arguments and then creates a Cafe
    # object, ready to be added to the Database.

    # The DB is made of string and boolean fields,
    # so some arguments must be converted to Boolean through a function.

    # Fetching strings from the request.
    cafe_name = request.args.get('name')
    cafe_map_url = request.args.get('map_url')
    cafe_img_url = request.args.get('img_url')
    cafe_location = request.args.get('location')
    cafe_seats = request.args.get('seats')
    cafe_coffee_price = request.args.get('coffee_price')

    # Fetching strings from the request and converting them to booleans.
    cafe_has_toilet = string_to_bool(request.args.get('has_toilet'))
    cafe_has_wifi = string_to_bool(request.args.get('has_wifi'))
    cafe_has_sockets = string_to_bool(request.args.get('has_sockets'))
    cafe_can_take_calls = string_to_bool(request.args.get('can_take_calls'))

    # Creating the Cafe Object
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

    try:
        # Creating a new Cafe to the Database.
        db.session.add(new_cafe)        # Adding the Cafe
        db.session.commit()             # Commiting the Change.
        return jsonify(response={"success": "Successfully added a new cafe!"})

    except exc.IntegrityError:
        # If Cafe already exists, the code returns an error JSON.
        return jsonify(error={"Duplicate Cafe": "Sorry! This Cafe already exists in our database."}), 409


@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    # "Update Price" routing. It fetches Cafe ID and price arguments,
    # then updates the DB if a valid Cafe was selected.

    # Fetching the Price Argument
    new_price = request.args.get('price')

    try:
        # The code now tries to update the price in the provided Cafe
        selected_cafe = db.session.query(Cafe).filter(Cafe.id == cafe_id).first()   # Query a Cafe
        selected_cafe.coffee_price = new_price                                      # Updating the Price
        db.session.commit()                                                         # Commiting the Change

        return jsonify(response={"success": "Successfully updated a price for your Cafe!"}), 200

    except AttributeError:
        # If the Caf?? is not found, it returns an error JSON.

        return jsonify(error={"Not Found": "Sorry! This Cafe was not found."}), 404


@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def close_cafe(cafe_id):
    # "Close Cafe" routing. It deletes a closed Cafe, but only if the request is valid.
    # It first checks if the provided Cafe and API Key are valid.

    try:
        # Checking if the Cafe exists by querying it from the Database
        selected_cafe = db.session.query(Cafe).filter(Cafe.id == cafe_id).first()

    except AttributeError:
        # If this exception is raised, Cafe doesn't exist!
        return jsonify(error={"Not Found": "Sorry! This Cafe was not found."}), 404

    # Testing the API Key and Cafe to Delete
    api_key = request.args.get('api_key')       # Grabbing the key from the request
    key_check = api_key_check(api_key)          # Checking if key is valid
    valid_cafe = cafe_check(cafe_id)            # Checking if cafe is valid

    # Function that confirms if it is okay to delete Cafe, based on the checks up above.
    delete_flag, delete_json, delete_http_code = confirm_delete(key_check, valid_cafe)

    # Taking the decision to delete the Cafe or not, based on confirm_delete function
    if delete_flag:
        # If deletion request is valid
        db.session.delete(selected_cafe)        # Deletes Cafe
        db.session.commit()                     # Commits the Change
        return delete_json, delete_http_code
    else:
        # If deletion request is invalid
        return delete_json, delete_http_code


# ---------------------------------- RUNNING ----------------------------------
if __name__ == '__main__':
    app.run(debug=True)
