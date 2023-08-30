# =======================================================================
# Project: Female Supervillain Trading Card App (REST API version)
# Description: An interactive web application built with Python.
# Built with: Flask and Flask-SQLAlchemy. The app's data is stored in an SQL database. The app uses a REST API and JavaScript to route and render data, and the jsonify function is used to convert and export data to ensure compatibility with the frontend.
# The app lets users:
# - add and delete female supervillain trading cards to/from a database.
# Background: Coursework for Skillcrush's "Using Python to Build Web Apps" course.

# ==== *** ====

# The main.py file contains the code that manages the logic of/operates the app. It:
# - creates the database model and manages interaction with the database.
# - contains routing for serving HTML files, querying the database, adding new villains to the database, and for deleting existing villains from the database.
# - handles error communication.
# - returns a response status.
# - contains an API directory listing the app's endpoints.
# =======================================================================

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask("app")
#Configures database root location and connects project to SQLAlchemy toolkit:
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///villain.db"
db = SQLAlchemy(app)


#Creates database model and columns:
class Villain(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=True, nullable=False)
  description = db.Column(db.String(120), nullable=False)
  interests = db.Column(db.String(250), nullable=False)
  url = db.Column(db.String(250), nullable=False)
  date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  #Specifies how to present the Villain object when called:
  def __repr__(self):
    return "<Villain " + self.name + ">"


#Creates database and commits changes:
with app.app_context():
  db.create_all()
  db.session.commit()


#### Serving Static Files
#Renders HTML for main villain page with all villains:
@app.route("/")
def villain_cards():
  return app.send_static_file("villain.html")


#Renders HTML for page where user adds a new villain to the database:
@app.route("/add")
def add():
  return app.send_static_file("addvillain.html")


#Renders HTML page where user deletes villain from database:
@app.route("/delete")
def delete():
  return app.send_static_file("deletevillain.html")


####


#Returns all the villains in the database:
@app.route("/api/villains/", methods=["GET"])
def get_villains():
  villains = Villain.query.all()
  #Adds data from database to villain cards:
  data = []
  for villain in villains:
    data.append({
      "name": villain.name,
      "description": villain.description,
      "interests": villain.interests,
      "url": villain.url,
      "date_added": villain.date_added
    })
  #Converts data list variable to a JSON object and returns to JavaScript:
  return jsonify(data)


#Adds new villain to database:
@app.route("/api/villains/add", methods=["POST"])
def add_villain():
  errors = []
  #Retrieves data sent from JavaScript:
  name = request.form.get("name")
  #Checks if villain info was submitted on HTML form and adds message to errors list if any info is missing:
  if not name:
    errors.append("Oops! Looks like you forgot a name!")

  description = request.form.get("description")
  if not description:
    errors.append("Oops! Looks like you forgot a description!")

  interests = request.form.get("interests")
  if not interests:
    errors.append("Oops! Looks like you forgot some interests!")

  url = request.form.get("url")
  if not url:
    errors.append("Oops! Looks like you forgot an image!")
  #Checks if new villain already exists in database:
  villain = Villain.query.filter_by(name=name).first()
  if villain:
    errors.append("Oops! A villain with that name already exists!")

  if errors:
    return jsonify({"errors": errors})
  #Adds new villain to database if no errors are found:
  else:
    new_villain = Villain(name=name,
                          description=description,
                          interests=interests,
                          url=url)
    db.session.add(new_villain)
    db.session.commit()
    #Success response status:
    return jsonify({"status": "success"})


#Removes existing villain from database:
@app.route("/api/villains/delete", methods=["POST"])
def delete_villain():
  #Retrieves data sent from JavaScript:
  name = request.form.get("name", "")
  #Checks if villain is in the database:
  villain = Villain.query.filter_by(name=name).first()
  if villain:
    db.session.delete(villain)
    db.session.commit()
    #Success response status:
    return jsonify({"status": "success"})
  else:
    return jsonify(
      {"errors": ["Oops! A villain with that name doesn't exist!"]})


#API directory:
@app.route("/api/", methods=["GET"])
def get_endpoints():
  endpoints = {
    "/api/villains/": "GET - Retrieves all villain data from the database",
    "/api/villains/delete":
    "POST - Removes an existing villain from the database",
    "/api/villains/add": "POST - Adds a new villain to the database"
  }
  return jsonify(endpoints)


app.run(host='0.0.0.0', port=8080)
