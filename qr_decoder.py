# program to detect and decode qr codes 

# importing OpenCV package
import cv2

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
    # data = decoded text, other two values are optional but we are adding points for detection
    data, points, _ = detector.detectAndDecode(frame)

    # if a QR code was found and decoded, print the data
    # {"package_id": "PKG-1", "name": "Jane Doe", "address": "1000 S Maple Ave, Miami, FL", "zip_code": "33101", "weight": "1.5lbs"}
    
    if data:
        print(data)

    state = data["address"].split(",")[-1].strip()
    print(state)
    
    # wait 1ms for a key press, if the user presses 'esc' then stop the loop
    if cv2.waitKey(1) == 27:
        break

camera.release()
