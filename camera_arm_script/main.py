import cv2
import json
from pyzbar.pyzbar import decode
import requests
from time import sleep, time
from arduino_interface import ArduinoInterface
from adafruit_servokit import ServoKit
import busio


class ConveyorController:

    CMD_STOP = b'S'
    CMD_GO = b'G'

    def __init__(self, arduino):
        self.arduino = arduino
        self.running = True

    def stop(self):
        print("Stopping conveyor")
        self.arduino.send(self.CMD_STOP)
        self.running = False

    def start(self):
        print("Starting conveyor")
        self.arduino.send(self.CMD_GO)
        self.running = True


API_URL = "http://10.0.192.208:5000/api/add-package"

east_coast = ("ME", "NH", "MA", "RI", "CT", "NY",
              "NJ", "DE", "MD", "VA", "NC", "SC", "GA", "FL")

west_coast = ("CA", "OR", "WA")


def main():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    arduino = ArduinoInterface(port='/dev/ttyACM0')
    conveyor = ConveyorController(arduino)

    SERVO_CHANNEL = 0

    i2c = busio.I2C(3, 2)
    kit = ServoKit(channels=16, i2c=i2c)
    kit.servo[SERVO_CHANNEL].set_pulse_width_range(500, 2500)

    scan_locked = False
    scan_start_time = None
    last_qr_data = None
    MAX_SCAN_TIME = 2.0

    while True:
        success, frame = camera.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        qr_codes = decode(gray)

        if qr_codes and not scan_locked:
            print("QR detected → stopping conveyor")
            conveyor.stop()
            sleep(0.3)
            scan_locked = True
            scan_start_time = time()

        if scan_locked:
            qr_codes = decode(gray)

            if qr_codes:
                qr = qr_codes[0]
                data = qr.data.decode('utf-8')

                if data != last_qr_data:
                    last_qr_data = data
                    print("Package data:", data)

                    try:
                        package = json.loads(data)

                        pkg_id = package.get("pkg_id", "")
                        name = package.get("name", "")
                        street_address = package.get("street_address", "")
                        city = package.get("city", "")
                        state = package.get("state", "")
                        zip_code = package.get("zip_code", "")
                        weight = package.get("weight", "")

                        print("State:", state)

                        if state in east_coast:
                            region = "EAST"
                            print("EAST COAST")
                            kit.servo[SERVO_CHANNEL].angle = 140
                            sleep(2)

                        elif state in west_coast:
                            region = "WEST"
                            print("WEST COAST")
                            kit.servo[SERVO_CHANNEL].angle = 55
                            sleep(2)

                        else:
                            region = "OTHER"
                            print("OTHER REGION")
                            kit.servo[SERVO_CHANNEL].angle = 180
                            sleep(1)

                        kit.servo[SERVO_CHANNEL].angle = 180

                        conveyor.start()
                        scan_locked = False

                        requests.post(API_URL, json={
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
                        print("Invalid QR JSON")

            elif time() - scan_start_time > MAX_SCAN_TIME:
                print("QR timeout → restarting conveyor")
                conveyor.start()
                scan_locked = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()