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


class ConveyorController:
    
    """Controls the conveyor belt via Arduino.

       The belt will stop when a package is detected so it can give the 
       servo time to sort the package 

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

API_URL = "http://10.0.192.208:5000/api/add-package"

# to determine which region the package is going to based on the state in the address
east_coast = ("ME", "NH", "MA", "RI", "CT", "NY", 
              "NJ", "DE", "MD", "VA", "NC", "SC", "GA", "FL")
west_coast = ("CA", "OR", "WA")


def main():
    camera = cv2.VideoCapture(0)

    arduino = ArduinoInterface(port='/dev/ttyACM0') 
    conveyor = ConveyorController(arduino)

    SERVO_CHANNEL = 0

    i2c = busio.I2C(3, 2)
    kit = ServoKit(channels=16, i2c=i2c)
    kit.servo[SERVO_CHANNEL].set_pulse_width_range(500, 2500)

    
    processed_qr_data = set()  # To track processed QR codes and avoid duplicates

    def move_west(kit, ch):
        kit.servo[ch].angle = 40

    def move_east(kit, ch):
        kit.servo[ch].angle = 125

    def reset(conveyor, kit, ch):
        kit.servo[ch].angle = 0
        conveyor.start()
   
  
    while True:
        success, frame = camera.read()
        if not success:
            break

        # decode QR codes in the frame
        qr_codes = decode(frame)
    
        for qr in qr_codes:
            data = qr.data.decode('utf-8')

            if data in processed_qr_data:
                continue
            
            processed_qr_data.add(data)

            print("Package data: " + data)

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

                # region logic
                if state in east_coast:
                    region = "EAST"
                    print("Package going to EAST COAST\n")

                    Timer(1.0, move_east, args=(kit, SERVO_CHANNEL)).start()
                    Timer(5.0, reset, args=(conveyor, kit, SERVO_CHANNEL)).start()

                elif state in west_coast:
                    region = "WEST"
                    print("Package going to WEST COAST\n")

                    Timer(1.0, move_west, args=(kit, SERVO_CHANNEL)).start()
                    Timer(5.0, reset, args=(conveyor, kit, SERVO_CHANNEL)).start()

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

            except json.JSONDecodeError:
                print("Error decoding JSON from QR code data: " + data)

        # q to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()