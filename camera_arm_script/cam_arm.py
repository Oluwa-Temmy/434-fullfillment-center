import cv2
import json
from pyzbar.pyzbar import decode
import requests
import serial
import serial.tools.list_ports
from time import sleep, time
from arduino_interface import ArduinoInterface

class ConveyorController:
    """Controls the conveyor belt via Arduino."""
    
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


class ServoController:
    """Controls a servo motor via Arduino."""
    
    # Command constants to send to Arduino
    CMD_WEST = b'W'
    CMD_EAST = b'E'
    CMD_CENTER = b'C'
    
    def __init__(self, arduino):
        """Initialize the servo controller.
        
        Args:
            arduino: ArduinoInterface instance for communication
        """
        self.arduino = arduino
    
    def move_west(self):
        """Send command to move servo to west position."""
        print("Sending WEST command to Arduino")
        self.arduino.send(self.CMD_WEST)
    
    def move_east(self):
        """Send command to move servo to east position."""
        print("Sending EAST command to Arduino")
        self.arduino.send(self.CMD_EAST)
    
    def move_center(self):
        """Send command to move servo to center position."""
        print("Sending CENTER command to Arduino")
        self.arduino.send(self.CMD_CENTER)
    
    def sort_package(self, direction):
        """Sort a package by sending the appropriate command to Arduino.
        
        The Arduino handles the timing and movement sequence.
        
        Args:
            direction: 'east', 'west', or 'center'
        """
        if direction == 'east':
            self.move_east()
        elif direction == 'west':
            self.move_west()
        else:
            self.move_center()


# Region definitions for package routing
EAST_COAST = ("ME", "NH", "MA", "RI", "CT", "NY",
              "NJ", "DE", "MD", "VA", "NC", "SC", "GA", "FL")
WEST_COAST = ("CA", "OR", "WA")


def detect_object(frame, bg_subtractor, min_area=5000):
    """Detect if a box-like package is present in the conveyor area."""
    h, w = frame.shape[:2]

    y1 = int(h * 0.45)
    y2 = int(h * 0.95)
    x1 = int(w * 0.15)
    x2 = int(w * 0.85)
    roi = frame[y1:y2, x1:x2]

    fg_mask = bg_subtractor.apply(roi)
    _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue

        x, y, bw, bh = cv2.boundingRect(cnt)
        if bh == 0:
            continue

        aspect_ratio = bw / float(bh)
        rect_area = bw * bh
        fill_ratio = area / float(rect_area) if rect_area else 0.0

        if 0.5 <= aspect_ratio <= 2.5 and fill_ratio >= 0.45:
            return True

    return False


def main():
    camera = cv2.VideoCapture(0)
    arduino = ArduinoInterface()
    servo = ServoController(arduino)
    conveyor = ConveyorController(arduino)
    
    QR_READ_TIMEOUT = 2.0  # Max seconds to try reading QR once stopped
    PRE_SCAN_RUN_SECONDS = 2.5  # Conveyor must run this long before scanning starts
    SERVO_DELAY = 0.25     # Seconds to wait after starting conveyor before moving servo
    API_URL = "http://10.0.192.208:5000/api/add-package"
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=50, detectShadows=False)
    package_detected = False
    detection_start_time = None
    last_qr_data = None
    last_conveyor_start_time = time()

    conveyor.start()
    
    while True:
        success, frame = camera.read()
        if not success:
            break

        ready_to_scan = (time() - last_conveyor_start_time) >= PRE_SCAN_RUN_SECONDS
        qr_codes = decode(frame) if ready_to_scan else []

        if not package_detected and ready_to_scan and detect_object(frame, bg_subtractor):
            package_detected = True
            detection_start_time = time()
            last_qr_data = None
            conveyor.stop()
            print("Object detected, conveyor stopped. Waiting for QR code...")
        
        if package_detected:
            elapsed = time() - detection_start_time
            
            if qr_codes:
                last_qr_data = qr_codes[0].data.decode('utf-8')

            if last_qr_data or elapsed >= QR_READ_TIMEOUT:
                if not last_qr_data:
                    print("No QR code detected in 2 seconds. Resuming conveyor.\n")
                    conveyor.start()
                    last_conveyor_start_time = time()
                    package_detected = False
                    detection_start_time = None
                    continue
                
                direction = 'center'  # Default
                
                if last_qr_data:
                    print("Package data: " + last_qr_data)
                    
                    try:
                        package = json.loads(last_qr_data)
                        pkg_id = package.get("pkg_id", "")
                        name = package.get("name", "")
                        street_address = package.get("street_address", "")
                        city = package.get("city", "")
                        state = package.get("state", "")
                        zip_code = package.get("zip_code", "")
                        weight = package.get("weight", "")
                        print("State: " + state)

                        if state in EAST_COAST:
                            print("Package going to EAST COAST\n")
                            direction = 'east'
                            region = "EAST"
                        elif state in WEST_COAST:
                            print("Package going to WEST COAST\n")
                            direction = 'west'
                            region = "WEST"
                        else:
                            print("Package going to OTHER REGION\n")
                            direction = 'center'
                            region = "OTHER"

                        address = ", ".join(
                            part for part in [street_address, city, f"{state} {zip_code}".strip()]
                            if part.strip()
                        )

                        requests.post(API_URL, json={
                            "Package ID": pkg_id,
                            "name": name,
                            "address": address,
                            "street_address": street_address,
                            "city": city,
                            "state": state,
                            "zip_code": zip_code,
                            "weight": weight,
                            "region": region
                        })

                    except json.JSONDecodeError:
                        print("Error: QR code data is not valid JSON\n")
                
                # Start conveyor first, then move servo after delay
                conveyor.start()
                last_conveyor_start_time = time()
                sleep(SERVO_DELAY)
                servo.sort_package(direction)
                
                # Reset for next package
                package_detected = False
                detection_start_time = None
                last_qr_data = None

        # Display camera feed
        cv2.imshow('Package Scanner', frame)

        # q to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
