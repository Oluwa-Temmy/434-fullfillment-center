import qrcode
import json

# ask for input package details 
pkg_id = input("Package ID: ")
name = input("Full Name: ")
street_address = input("Street Address: (e.g. 123 Main St): ")
city = input("City: ")
state = input("State (e.g. CA): ")
zip_code = input("Zip Code: ")
weight = input("Weight (e.g. 3.2): ")

# turn package details into a dictionary
data = {
    "package_id": pkg_id,
    "name": name,
    "street_address": street_address,
    "city": city,
    "state": state,
    "zip_code": zip_code,
    "weight": f"{weight}lbs"
}

# generate QR code from the package details as a JSON string and save it as an image file
img = qrcode.make(json.dumps(data))
img.save(f"{pkg_id}.png")

print(f"QR code generated: {pkg_id}.png")
