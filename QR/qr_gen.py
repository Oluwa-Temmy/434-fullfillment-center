import random
import qrcode
import json

first_names = ["James", "Sarah", "Mike", "Emily", "John", "Ashley", "David", "Jessica", 
               "Robert", "Linda", "Michael", "Barbara", "William", "Elizabeth", "Richard", "Jennifer"]

last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
              "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris"]


east_coast_cities = [
    "Portland", "Providence", "Hartford", "Baltimore", "Richmond", "Raleigh", "Charleston"
]

east_coast_states = [
    "ME",
    "RI",
    "CT",
    "MD",
    "VA",
    "NC",
    "SC"
]

east_coast_zip_codes = [
    "04101",
    "02901",
    "06101",
    "21201",
    "23218",
    "27601",
    "29401"
]

west_coast_cities = [
    "San Diego", "San Jose", "Sacramento", "Eugene", "Spokane", "Boise", "Reno"
]
west_coast_states = [
    "CA",
    "WA",
    "OR"
]
west_coast_zip_codes = [
    "90001",
    "98101",
    "94101",
    "97201"
]


streets = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Elm St", "Park Blvd", 
           "Pine St", "Spruce Ave", "Birch Dr", "Willow Ln"]

def generate_package():
    pkg_id = f"PKG-{random.randint(10000, 99999)}"
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    if random.random() < 0.5:
        city = random.choice(east_coast_cities)
        state = random.choice(east_coast_states)
        zip_code = random.choice(east_coast_zip_codes)
    else:
        city = random.choice(west_coast_cities)
        state = random.choice(west_coast_states)
        zip_code = random.choice(west_coast_zip_codes)

    street = f"{random.randint(100, 9999)} {random.choice(streets)}"
    weight = round(random.uniform(0.5, 50.0), 2)

    package_data = {
        "pkg_id": pkg_id,
        "name": name,
        "street_address": f"{street}",
        "city": f"{city}",
        "state": f"{state}",
        "zip_code": f"{zip_code}",
        "weight": f"{weight}lbs"
    }
    

    
    img = qrcode.make(json.dumps(package_data))
    img.save(f"{pkg_id}.png")

    print(f"QR code generated: {pkg_id}.png")
    
# Generate 10 test QR codes
for _ in range(10):
    generate_package()
   
