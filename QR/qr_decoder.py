import cv2
import json
from pyzbar.pyzbar import decode

""" Our INITIAL decoding script for QR codes, which was implemented in the main camera arm script

This is a SEPERATE file we used to first test the QR code decoding logic to ensure it worked as expected 
BEFORE integrating it into the main script. """

# Uses pyzbar library to decode QR codes from camera feed.

# List of states for east and west coast regions
east_coast = ("ME", "NH", "MA", "RI", "CT", "NY", 
              "NJ", "DE", "MD", "VA", "NC", "SC", "GA", "FL", "IL", "PA", "WV")
west_coast = ("CA", "OR", "WA", "AK", "HI")

# defining what camera is capturing footage (on the RPi, 0 is the webcam connected to the USB port)
camera = cv2.VideoCapture(0)


# loop that holds camera processing and QR code decoding logic 
# runs until we break out of it 

while True:
    # read a frame from the camera
    success, frame = camera.read()
    # if no frame, stop loop
    if not success:
        break

    # decode QR codes in the frame
    qr_codes = decode(frame)

    # if QR codes are found, print the data and determine the region based on the state
    for qr in qr_codes:
        data = qr.data.decode('utf-8')
        print("Package data: " + data)

        # data expected to be in JSON format
        # try to parse it and extract the address information
        try:
            package = json.loads(data)
            street = package.get("street_address", "")
            city = package.get("city", "")
            state = package.get("state", "")
            address = f"{street}, {city}, {state}"
            print("State: " + state)

            # determine region based on state and print 
            if state in east_coast:
                print("Package going to EAST COAST\n")
            elif state in west_coast:
                print("Package going to WEST COAST\n")
            else:
                print("Package going to OTHER REGION\n")


        except json.JSONDecodeError:
            print("Error: QR code data is not valid JSON\n")

    # q to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
