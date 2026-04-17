import cv2
import json
from pyzbar.pyzbar import decode
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


def main():
    camera = cv2.VideoCapture(0)
    arduino = ArduinoInterface()
    servo = ServoController(arduino)
    conveyor = ConveyorController(arduino)
    
    QR_READ_TIMEOUT = 2.0  # Max seconds to try reading QR
    SERVO_DELAY = 0.25     # Seconds to wait after starting conveyor before moving servo
    API_URL = "http://10.0.192.208:5000/api/packages"
    package_detected = False
    detection_start_time = None
    last_qr_data = None
    
    while True:
        success, frame = camera.read()
        if not success:
            break

        # decode QR codes in the frame
        qr_codes = decode(frame)

        if qr_codes and not package_detected:
            # First detection - stop conveyor and start timer
            package_detected = True
            detection_start_time = time()
            conveyor.stop()
            print("Package detected, reading QR code...")
        
        if package_detected:
            elapsed = time() - detection_start_time
            
            # Try to read QR data
            if qr_codes:
                qr = qr_codes[0]
                last_qr_data = qr.data.decode('utf-8')
                
                # Draw rectangle around QR code
                points = qr.polygon
                if points:
                    pts = [(p.x, p.y) for p in points]
                    for i in range(len(pts)):
                        cv2.line(frame, pts[i], pts[(i+1) % len(pts)], (0, 255, 0), 3)
            
            # Process after timeout OR if we have valid data
            if elapsed >= QR_READ_TIMEOUT or (last_qr_data and elapsed >= 0.5):
                print(f"Processing after {elapsed:.1f}s")
                
                direction = 'center'  # Default
                
                if last_qr_data:
                    print("Package data: " + last_qr_data)
                    
                    try:
                        package = json.loads(last_qr_data)
                        address = package.get("address", "")
                        state = address.split(",")[-1].strip()
                        print("State: " + state)

                        if state in EAST_COAST:
                            print("Package going to EAST COAST\n")
                            direction = 'east'
                        elif state in WEST_COAST:
                            print("Package going to WEST COAST\n")
                            direction = 'west'
                        else:
                            print("Package going to OTHER REGION\n")
                            direction = 'center'

                    except json.JSONDecodeError:
                        print("Error: QR code data is not valid JSON\n")
                else:
                    print("Could not read QR code, moving to center\n")
                
                # Start conveyor first, then move servo after delay
                conveyor.start()
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
