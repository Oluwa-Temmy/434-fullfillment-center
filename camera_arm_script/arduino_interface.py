import serial
import serial.tools.list_ports
from time import sleep

""" Script to handle communication with the Arduino controlling the DC motor for the belt """

""" Using the pyserial library to handle serial communication with the Arduino. 

    ArduinoInterface class (from the pyserial library) provides the methods to connect to the 
    Arduino, send and receive data, and manage the serial connection. """

class ArduinoInterface:
    
    def __init__(self, port=None, baudrate=9600, timeout=1):
        """Initialize the Arduino serial connection.
        
        Args:
            port: Serial port name (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux).
                  If None, will attempt to auto-detect Arduino.
            baudrate: Serial communication speed (default 9600)
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
        
        Returns:
            Port name if found, None otherwise.
        """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Common Arduino identifiers
            if 'Arduino' in port.description or 'CH340' in port.description or 'USB Serial' in port.description:
                return port.device
        # Return first available port as fallback
        if ports:
            return ports[0].device
        return None
    
    def _connect(self):
        """Establish serial connection to Arduino."""
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
        """Check if Arduino is connected.
        
        Returns:
            True if connected, False otherwise.
        """
        return self.serial is not None and self.serial.is_open
    
    def send(self, data):
        """Send data to the Arduino.
        
        Args:
            data: Bytes or string to send
        """
        if self.is_connected():
            if isinstance(data, str):
                data = data.encode()
            self.serial.write(data)
            self.serial.flush()
    
    def read(self, size=1):
        """Read data from the Arduino.
        
        Args:
            size: Number of bytes to read
            
        Returns:
            Bytes read from Arduino, or None if not connected.
        """
        if self.is_connected():
            return self.serial.read(size)
        return None
    
    def readline(self):
        """Read a line from the Arduino.
        
        Returns:
            Line read from Arduino, or None if not connected.
        """
        if self.is_connected():
            return self.serial.readline().decode().strip()
        return None
    
    def close(self):
        """Close the serial connection."""
        if self.is_connected():
            self.serial.close()
            print("Arduino connection closed")
    
    def __del__(self):
        """Cleanup serial connection on object destruction."""
        self.close()
