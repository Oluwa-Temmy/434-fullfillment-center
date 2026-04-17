from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import datetime
 
# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# route to the home page that renders the home.html template
@app.route("/")
def index():
    return render_template("home.html")

# Configure the SQLite database and initialize SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///packages.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# create the SQLAlchemy database instance
db = SQLAlchemy(app)

# Define the Package model for the database
class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    state = db.Column(db.String(10))
    region = db.Column(db.String(20))  # EAST / WEST / OTHER
    ship_date = db.Column(db.DateTime, default=datetime.datetime.now)
    delivery_date = db.Column(db.DateTime)

# Create the database tables
with app.app_context():
    db.create_all()

# API endpoint to get all packages in JSON format
@app.route("/api/packages")
def get_packages():
    packages = Package.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "address": p.address,
        "state": p.state,
        "region": p.region,
        "ship_date": p.ship_date.isoformat(),
        "delivery_date": p.delivery_date.isoformat()
    } 
    for p in packages
    ])

# API endpoint to add a new package via POST request
@app.route("/api/add-package", methods=["POST"])
def add_package():
    # Get the JSON data from the request
    data = request.get_json()
    ship_date = datetime.datetime.now()
    


    #Create a new Package instance with the provided data
    new_package = Package(
        name=data.get("name", ""),
        address=data.get("address", ""),
        state=data.get("state", ""),
        region=data.get("region", ""),
        ship_date=ship_date,
        delivery_date=ship_date + datetime.timedelta(days=14)
    )

    db.session.add(new_package)
    db.session.commit()

    return jsonify({
        "message": "Package added successfully",
        "id": new_package.id
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
