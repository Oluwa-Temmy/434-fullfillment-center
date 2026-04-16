from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import datetime
 

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("home.html")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///packages.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    state = db.Column(db.String(10))
    region = db.Column(db.String(20))  # EAST / WEST / OTHER
    ship_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    delivery_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()


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

@app.route("/api/add-package", methods=["POST"])
def add_package():
    # Get the JSON data from the request
    data = request.get_json()

    #Create a new Package instance with the provided data
    new_package = Package(
        name=data.get("name"),
        address=data.get("address"),
        state=data.get("state"),
        region=data.get("region")
    )

    db.session.add(new_package)
    db.session.commit()

    return jsonify({
        "message": "Package added successfully",
        "id": new_package.id
    }), 201


if __name__ == "__main__":
    app.run(debug=True)
