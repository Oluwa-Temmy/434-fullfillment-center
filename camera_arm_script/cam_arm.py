import cv2
import json
from pyzbar.pyzbar import decode
from gpiozero import Servo
from time import sleep

# to determine which region the package is going to based on the state in the address
east_coast = ("ME", "NH", "MA", "RI", "CT", "NY", 
              "NJ", "DE", "MD", "VA", "NC", "SC", "GA", "FL")
west_coast = ("CA", "OR", "WA")

camera = cv2.VideoCapture(0)

# GPIO pin for the servo motor on Rpi 
myGPIO = 18

servo = Servo(myGPIO)
servo.value = None

WEST = -0.2
EAST = 0.98
CENTER = 0.5

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
                servo.value = EAST
                sleep(.75) # to allow the servo to move before processing the next package
                servo.value = CENTER
                sleep(.75) # to allow the servo to move back to center before processing the next package
                servo.value = None # to reset the servo position for the next package


            elif state in west_coast:
                print("Package going to WEST COAST\n")
                servo.value = WEST
                sleep(.75)
                servo.value = CENTER
                sleep(.75)
                servo.value = None
                
            else:
                print("Package going to OTHER REGION\n")
                servo.value = CENTER

        except json.JSONDecodeError:
            print("Error: QR code data is not valid JSON\n")

    # q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()






