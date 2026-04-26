import random
import qrcode
import json
import uuid

""" 
This script generates QR codes for packages with random data. Each package has a unique ID,
a random name, a random address (street, city, state, zip code), and a random weight. 

The QR code is saved as a PNG file with the package ID as the filename.
"""

# first and last names for random generation
first_names = ["James", "Sarah", "Mike", "Emily", "John", "Ashley", "David", "Jessica", 
               "Robert", "Linda", "Michael", "Barbara", "William", "Elizabeth", "Richard", "Jennifer"]

last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
              "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris"]

# east, west, and other locations for random generation
east_coast_locations = [
    ("Portland", "ME"),
    ("Manchester", "NH"),
    ("Providence", "RI"),
    ("Baltimore", "MD"),
    ("Richmond", "VA"),
    ("Raleigh", "NC"),
    ("Charleston", "SC"),
    ("Miami", "FL"),
    ("Philadelphia", "PA"),
    ("Boston", "MA"),
    ("New York City", "NY"),
    ("Newark", "NJ"),
    ("Wilmington", "DE"),
    ("Hartford", "CT")
]

west_coast_locations = [
    ("San Diego", "CA"),
    ("San Jose", "CA"),
    ("Sacramento", "CA"),
    ("Eugene", "OR"),
    ("Spokane", "WA"),
    ("Boise", "ID"),
    ("Reno", "NV")
]

other_locations = [
    ("Chicago", "IL"),
    ("Houston", "TX"),
    ("Phoenix", "AZ"),
    ("Las Vegas", "NV"),
    ("Denver", "CO"),
    ("Salt Lake City", "UT"),
    ("Albuquerque", "NM"),
    ("Cheyenne", "WY")
]

# common street names for random generation
streets = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Elm St", "Park Blvd", 
           "Pine St", "Spruce Ave", "Birch Dr", "Willow Ln", "Ash St", "Cherry Ave", 
           "Walnut Dr", "Poplar Ln", "Hickory St", "Sycamore Ave", "Magnolia Dr", 
           "Dogwood Ln", "Cypress St", "Redwood Ave"]

# Function to generate a random package and create a QR code for it
def generate_package():
    pkg_id = f"PKG-{uuid.uuid4()}" # UUID used to ensure unique package IDs

    # Randomly generate a name by combining a random first name and a random last name
    name = f"{random.choice(first_names)} {random.choice(last_names)}" 

    location_type = random.choice(["east", "west"])

    if location_type == "east":
        city, state = random.choice(east_coast_locations)
    else:
        city, state = random.choice(west_coast_locations)

    zip_code = f"{random.randint(10000, 99999)}"

    street = f"{random.randint(100, 9999)} {random.choice(streets)}"
    weight = round(random.uniform(0.5, 50.0), 2)

    package_data = {
        "pkg_id": pkg_id,
        "name": name,
        "street_address": street,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "weight": f"{weight}lbs"
    }

    img = qrcode.make(json.dumps(package_data))
    img.save(f"{pkg_id}.png")

    print(f"QR code generated: {pkg_id}.png")


# Generate 8 test QR codes
for _ in range(8):
    generate_package()