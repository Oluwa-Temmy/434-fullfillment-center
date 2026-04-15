from flask import Flask, jsonify
from flask_cors import CORS
from flask import render_template 


app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("home.html")


packages = [
    {"id": 0,  "first": "James",   "last": "Harrington", "address": "142 Maple Ave",   "state": "New York",      "coast": "East", "ship_date": "2026-04-02"},
    {"id": 1,  "first": "Sofia",   "last": "Reyes",       "address": "89 Ocean Blvd",   "state": "California",    "coast": "West", "ship_date": "2026-04-05"},
    {"id": 2,  "first": "Marcus",  "last": "Chen",        "address": "330 Pine St",      "state": "Massachusetts", "coast": "East", "ship_date": "2026-04-03"},
    {"id": 3,  "first": "Layla",   "last": "Williams",    "address": "77 Sunset Dr",    "state": "Oregon",        "coast": "West", "ship_date": "2026-04-08"},
    {"id": 4,  "first": "Ethan",   "last": "Brooks",      "address": "21 Harbor Rd",    "state": "Florida",       "coast": "East", "ship_date": "2026-04-01"},
    {"id": 5,  "first": "Priya",   "last": "Nair",        "address": "5 Redwood Ln",    "state": "Washington",    "coast": "West", "ship_date": "2026-04-06"},
    {"id": 6,  "first": "Noah",    "last": "Fitzgerald",  "address": "460 Elm St",      "state": "Connecticut",   "coast": "East", "ship_date": "2026-04-10"},
    {"id": 7,  "first": "Camille", "last": "Dubois",      "address": "19 Mesa Way",     "state": "Arizona",       "coast": "West", "ship_date": "2026-04-04"},
    {"id": 8,  "first": "Derek",   "last": "Okafor",      "address": "88 Liberty Pl",   "state": "New Jersey",    "coast": "East", "ship_date": "2026-04-07"},
    {"id": 9,  "first": "Hannah",  "last": "Park",        "address": "302 Crest Blvd",  "state": "Nevada",        "coast": "West", "ship_date": "2026-04-09"},
    {"id": 10, "first": "Leo",     "last": "Kowalski",    "address": "54 Birch Ct",     "state": "Pennsylvania",  "coast": "East", "ship_date": "2026-04-11"},
    {"id": 11, "first": "Amara",   "last": "Singh",       "address": "11 Cliff Rd",     "state": "Idaho",         "coast": "West", "ship_date": "2026-04-12"},
]


@app.route("/api/packages", methods=["GET"])
def get_packages():
    """
    Returns all packages.
    Supports optional query params:
      - coast=East|West
      - date_from=YYYY-MM-DD
      - date_to=YYYY-MM-DD
    Filtering by name/state is handled client-side.
    """
    from flask import request

    coast = request.args.get("coast")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    results = packages

    if coast in ("East", "West"):
        results = [p for p in results if p["coast"] == coast]

    if date_from:
        results = [p for p in results if p["ship_date"] >= date_from]

    if date_to:
        results = [p for p in results if p["ship_date"] <= date_to]

    return jsonify(results)


@app.route("/api/packages/<int:package_id>", methods=["GET"])
def get_package(package_id):
    """Returns a single package by its shipping ID."""
    package = next((p for p in packages if p["id"] == package_id), None)
    if package is None:
        return jsonify({"error": "Package not found"}), 404
    return jsonify(package)


if __name__ == "__main__":
    app.run(debug=True)
