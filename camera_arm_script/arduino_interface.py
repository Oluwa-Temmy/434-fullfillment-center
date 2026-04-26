import serial
import serial.tools.list_ports
from time import sleep

 """This script handles serial communication between an Arduino and the raspberry pi.
    The arduino controls the DC motor. The raspberry pi sends commands to the arduino for when to start and stop the belt."""
    

class ArduinoInterface:
    """ this class ahngles the communication with the arduino. 
    It detects the port, sends commands to arduino and establishes and closes serial connection.
   """
    
    def __init__(self, port=None, baudrate=9600, timeout=1):
        """Initializes the Arduino serial connection.
        
        Args:
            port: Serial port name (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux).
                  If None, will try to automatically detect the Arduino port.
            baudrate: this is the serial communication speed (default 9600) between the pi and the arduino.
            timeout: Serial read timeout in seconds
        """
        
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.port = port
        
        if self.port is None:
            self.port = self._find_arduino()
        
        self._connect()
    
    def _find_arduino(self):
        """Auto-detect Arduino serial port.

        This checks all the available serial ports and checks to see if there's any common arduino identifiers. 
        
        Returns:
            Port name if found, returns None if no arduino is found.
        """
        
        ports = serial.tools.list_ports.comports()
        for port in ports:
            """ listed below are the most Common Arduino identifiers """
            if 'Arduino' in port.description or 'CH340' in port.description or 'USB Serial' in port.description:
                return port.device
                
        """ if there are no arduino identifiers then it Returns the first available port as fallback"""
        
        if ports:
            return ports[0].device
        return None
    
    def _connect(self):
        
        """This establishes serial connection to Arduino. If a valid port is found, the serial connection is established
        and it waits 2 seconds for the arduino to reset. """
        
        if self.port:
            try:
                self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                sleep(2)  # Wait for Arduino to reset after serial connection
                print(f"Connected to Arduino on {self.port}")
            except serial.SerialException as e:
                print(f"Error connecting to Arduino: {e}")
        else:
            print("Warning: No Arduino found. Running in simulation mode.")
    
    def is_connected(self):
        """this checks if Arduino is connected.
        
        Returns:
            True if connected, False if not connected
        """
        return self.serial is not None and self.serial.is_open
    
    def send(self, data):
        """This sends data to the Arduino. this is used to send conveyor commands go or stop.
        
        Args:
            data: Bytes or string to send. will either send 'G' for go or 'S' for stop conveyor
        """
        if self.is_connected():
            if isinstance(data, str):
                data = data.encode()
            self.serial.write(data)
            self.serial.flush()
    
    def read(self, size=1):
        """This reads data from the Arduino.
        
        Args:
            size: Number of bytes to read
            
        Returns:
            Bytes read from Arduino, or returns None if not connected.
        """
        if self.is_connected():
            return self.serial.read(size)
        return None
    
    def readline(self):
        """This reads a line from the Arduino. 
        This is used if the arduino sends status messages or sensor values to the pi.
        
        Returns:
            the decoded line read from the arduino, or None if not connected.
        """
        if self.is_connected():
            return self.serial.readline().decode().strip()
        return None
    
    def close(self):
        """This safely closes the serial connection. and prevents issues with the port locking."""
        if self.is_connected():
            self.serial.close()
            print("Arduino connection closed")
    
    def __del__(self):
        """this automatically cleans up the serial connection once an object is destroyed."""
        self.close()
