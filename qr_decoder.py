import cv2
import json
from pyzbar.pyzbar import decode

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
            address = package.get("address", "")
            state = address.split(",")[-1].strip()
            print("State: " + state)

            if state in east_coast:
                print("Package going to EAST COAST\n")
            elif state in west_coast:
                print("Package going to WEST COAST\n")
            else:
                print("Package going to OTHER REGION\n")

        except json.JSONDecodeError:
            print("Error: QR code data is not valid JSON\n")

    # q to quit
    cv2.imshow("QR Scanner", frame) # to view camera feed 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()


"""# program to detect and decode qr codes 

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
        print("package data: " + data + "\n")

        package = json.loads(data)
        address = package["address"]

        state = address.split(",")[-1].strip()
        print("State: " + state + "\n")
  
        if state in east_coast:
            print("Package going to EAST COAST\n")

        elif state in west_coast:
            print("Package going to WEST COAST\n")

        else:
            print("Package going to OTHER REGION")

camera.release() """
