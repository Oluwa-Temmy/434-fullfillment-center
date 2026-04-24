import random
import qrcode
import json
import uuid

first_names = ["James", "Sarah", "Mike", "Emily", "John", "Ashley", "David", "Jessica", 
               "Robert", "Linda", "Michael", "Barbara", "William", "Elizabeth", "Richard", "Jennifer"]

last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
              "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris"]


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

streets = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Elm St", "Park Blvd", 
           "Pine St", "Spruce Ave", "Birch Dr", "Willow Ln", "Ash St", "Cherry Ave", 
           "Walnut Dr", "Poplar Ln", "Hickory St", "Sycamore Ave", "Magnolia Dr", 
           "Dogwood Ln", "Cypress St", "Redwood Ave"]

def generate_package():
    pkg_id = f"PKG-{uuid.uuid4()}"
    name = f"{random.choice(first_names)} {random.choice(last_names)}"

    location_type = random.choice(["east", "west", "other"])

    if location_type == "east":
        city, state = random.choice(east_coast_locations)
    elif location_type == "west":
        city, state = random.choice(west_coast_locations)
    else:
        city, state = random.choice(other_locations)

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