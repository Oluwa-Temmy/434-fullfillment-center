import cv2
import json
from pyzbar.pyzbar import decode
import requests
import serial
import serial.tools.list_ports
from time import sleep, time
from arduino_interface import ArduinoInterface
from adafruit_servokit import ServoKit
import busio
from threading import Timer

""" This is our main script responsible for decoding qr codes and parsing them into JSON to send 
    them to the database, controlling the servo arm position and conveyor belt.
"""


""" The conveyor belt is controlled via an Arduino, we send commands to start and stop the belt."""

class ConveyorController:
    
    """Controls the conveyor belt via Arduino.

       The belt will stop when a package is detected so it can give the 
       servo time to sort the package.

    """

    CMD_STOP = b'S'
    CMD_GO = b'G'
    
    def __init__(self, arduino):
        """Initialize the conveyor controller.
        
        Args:
            arduino: ArduinoInterface instance for communication
        """
        self.arduino = arduino
        self.running = True
    
    def stop(self):
        """Stop the conveyor belt."""
        print("Stopping conveyor")
        self.arduino.send(self.CMD_STOP)
        self.running = False
    
    def start(self):
        """Start the conveyor belt."""
        print("Starting conveyor")
        self.arduino.send(self.CMD_GO)
        self.running = True


""" Servo controll code for the arm that will sort the packages will 
move via Raspberry Pi GPIO pins to control the servo motor """


# API endpoint where package data is sent after processing the QR code
# so it can be stored in the database
API_URL = "http://10.0.192.208:5000/api/add-package"

# to determine which region the package is going to based on the state in the address
east_coast = ("ME", "NH", "MA", "RI", "CT", "NY", 
              "NJ", "DE", "MD", "VA", "NC", "SC", "GA", "FL")
west_coast = ("CA", "OR", "WA")

"""
Main function to capture video, decode QR codes, and control the conveyor 
and servo based on the package data

"""
def main():

    # Initialize the camera. USB webcam on our RPi4 is at index 0
    camera = cv2.VideoCapture(0)

    """
    Initialize the Arduino interface and conveyor controller

    this is for the DC motor to stop the conveyor belt 
    when a package is detected so the servo has time to sort the package
    
    """
    arduino = ArduinoInterface(port='/dev/ttyACM0') 
    conveyor = ConveyorController(arduino)

    # Servo channel set to 0 for the PCA9685 servo controller 
    SERVO_CHANNEL = 0

    # Initialize the servo controller using I2C communication 
    # Ray helped us with the set up and wiring for this part
    i2c = busio.I2C(3, 2)
    kit = ServoKit(channels=16, i2c=i2c)
    kit.servo[SERVO_CHANNEL].set_pulse_width_range(500, 2500)

    # To track processed QR codes and avoid duplicates
    processed_qr_data = set()  

    """
    Functions to move the servo arm to sort packages to the east or west coast bins.

    Implemented as the servo needs to be moved back to the center position after sorting 
    each package. 

    Using sleep() did not work because it stopped the entire program. 
    Instead, Timer was used from the threading package.
    """
    def move_west(kit, ch):
        kit.servo[ch].angle = 40

    def move_east(kit, ch):
        kit.servo[ch].angle = 130

    def reset(conveyor, kit, ch):
        kit.servo[ch].angle = 0
        
   
    # Main loop to capture video frames and process QR codes until it is stopped by the user
    while True:
        success, frame = camera.read()
        if not success:
            break

        # decode QR codes in the frame
        qr_codes = decode(frame)
    
        # Process each detected QR code
        for qr in qr_codes:
            data = qr.data.decode('utf-8')
            
            # Skip processing if this QR code data has already been processed
            if data in processed_qr_data:
                continue
            
            # Add the new QR code data to the set of processed data
            processed_qr_data.add(data)
            
            print("Package data: " + data)

            # try to parse the QR code data as JSON and extract package information
            try:
                package = json.loads(data)

                pkg_id = package.get("pkg_id", "")
                name = package.get("name", "")
                street_address = package.get("street_address", "")
                city = package.get("city", "")
                state = package.get("state", "")
                zip_code = package.get("zip_code", "")
                weight = package.get("weight", "")

                print("State: " + state)

                # region and servo control logic
                # check if the pasred state is in the east or west coast tuples to determine 
                # where the package is going and move the servo arm accordingly

                if state in east_coast:
                    region = "EAST"
                    print("Package going to EAST COAST\n")

                    """conveyor.stop() is called to stop the conveyor belt 
                    so the servo has time to sort the package before the next one comes in."""
                    conveyor.stop()  

                    """0.3 seconds after the conveyor is stopped, the move_east function is called 
                    to move the servo arm to the position for sorting packages to the east coast bin.
                    """
                    Timer(.3, move_east, args=(kit, SERVO_CHANNEL)).start()

                    """After 0.6 seconds, the conveyor is started again to so the package moves 
                    toward the arm and gets directed toward the correct bin."""
                    Timer(0.6, conveyor.start).start()   

                    """After 15 seconds, the reset function is called to move the servo back 
                    to the center position and get ready for the next package."""

                    Timer(15.0, reset, args=(conveyor, kit, SERVO_CHANNEL)).start()



                    """ West coast logic is the same as east coast, but with different servo angle 
                    for sorting to the west coast bin.

                    Has a shorter reset time since the west coast bin is closer to the arm than 
                    the east coast bin."""

                elif state in west_coast:
                    region = "WEST"
                    print("Package going to WEST COAST\n")
                    conveyor.stop() 
                    Timer(0.3, move_west, args=(kit, SERVO_CHANNEL)).start()
                    Timer(0.6, conveyor.start).start()
                    Timer(10.0, reset, args=(conveyor, kit, SERVO_CHANNEL)).start()
                

                
                    """ If the state is not in either the east or 
                        west coast tuples, it is categorized as "OTHER.
                        
                        The servo does not need to move for these packages since 
                        they are going to the bin straight ahead.
                        """
                else:
                    region = "OTHER"
                    print("Package going to OTHER REGION\n")

                    Timer(1.0, reset, args=(conveyor, kit, SERVO_CHANNEL)).start()
                    

                # Send the package data to the API
                response = requests.post(API_URL, json={
                    "Package ID": pkg_id,
                    "name": name,
                    "street_address": street_address,
                    "city": city,
                    "state": state,
                    "zip_code": zip_code,
                    "weight": weight,
                    "region": region
                })

            # Handle JSON decoding errors if the QR code data is not in the expected format
            except json.JSONDecodeError:
                print("Error decoding JSON from QR code data: " + data)

        # to quit program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    camera.release()
    cv2.destroyAllWindows()

# Run the main function when the script is executed
if __name__ == "__main__":
    main()