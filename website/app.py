from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import datetime
 

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("home.html")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///packages.db'
db = SQLAlchemy(app)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    state = db.Column(db.String(10))
    region = db.Column(db.String(20))  # EAST / WEST / OTHER
    ship_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    devlivery_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

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
        "devlivery_date": p.devlivery_date.isoformat()
    } 
    for p in packages
    ])




if __name__ == "__main__":
    app.run(debug=True)
