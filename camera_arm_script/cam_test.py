import cv2
import json
from pyzbar.pyzbar import decode
# from gpiozero import Servo
from time import sleep
import requests

API_URL = "http://127.0.0.1:5000/api/add-package"

# to determine which region the package is going to based on the state in the address
east_coast = ("ME", "NH", "MA", "RI", "CT", "NY", 
              "NJ", "DE", "MD", "VA", "NC", "SC", "GA", "FL")
west_coast = ("CA", "OR", "WA")

camera = cv2.VideoCapture(0)


while True:
    success, frame = camera.read()
    if not success:
        break

    # decode QR codes in the frame
    qr_codes = decode(frame)

    for qr in qr_codes:
        data = qr.data.decode('utf-8')
        print("Package data: " + data)

        try:
            package = json.loads(data)
            name = package.get("name", "")
            address = package.get("address", "")
            state = address.split(",")[-1].strip()
            print("State: " + state)

        # region logic
            if state in east_coast:
                region = "EAST"
                print("Package going to EAST COAST\n")
               

            elif state in west_coast:
                region = "WEST"
                print("Package going to WEST COAST\n")
                
                
            else:
                region = "OTHER"
                print("Package going to OTHER REGION\n")

            # Send the package data to the API
            response = requests.post(API_URL, json={
                "name": name,
                "address": address,
                "state": state,
                "region": region
            })

        except json.JSONDecodeError:
            print("Error: QR code data is not valid JSON\n")

    # q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()