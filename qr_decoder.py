# program to detect and decode qr codes 

# importing OpenCV package
import cv2
import json

east_coast = ("ME", "NH", "MA", "RI", "CT", "NY", 
              "NJ", "DE", "MD", "VA", "NC", "SC", "GA", "FL")

west_coast = ("CA", "OR", "WA")

# defining what camera is capturing footage
camera = cv2.VideoCapture(0)

# creating a QR code detector object
detector = cv2.QRCodeDetector()

# loop runs forever until we break out of it (with esc key)
while True:
    # read a frame from the camera
    # success = True if frame was grabbed, frame = the actual image
    success, frame = camera.read()
    
    # if no frame, stop loop
    if not success:
        break

    # try to find and decode a QR code in the frame
    # data = decoded text, other two values we don't need
    data, _, _ = detector.detectAndDecode(frame)

    # if a QR code was found and decoded, print the data
    if data:
        print(data)

        package = json.loads(data)
        address = package["address"]

        state = address.split(",")[-1].strip()

        if state in east_coast:
            print("Package going to EAST COAST")

        elif state in west_coast:
            print("Package going to WEST COAST")

        else:
            print("Package going to OTHER REGION")

camera.release()
