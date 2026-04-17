#include <Servo.h>

// Motor pins
int motorSpeedPin = 3;
int motorDirectionPin1 = 4;
int motorDirectionPin2 = 5;

// Servo setup
Servo sortingServo;
int servoPin = 9;

// Servo positions (adjust these values as needed)
int WEST_POSITION = 45;
int CENTER_POSITION = 90;
int EAST_POSITION = 135;

// Timing
int MOVE_DELAY = 750;  // ms to wait after moving servo

// Conveyor state
bool conveyorRunning = true;
int motorSpeed = 110;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Motor pins
  pinMode(motorSpeedPin, OUTPUT);
  pinMode(motorDirectionPin1, OUTPUT);
  pinMode(motorDirectionPin2, OUTPUT);
  
  // Attach servo
  sortingServo.attach(servoPin);
  sortingServo.write(CENTER_POSITION);
}

void startConveyor() {
  conveyorRunning = true;
  analogWrite(motorSpeedPin, motorSpeed);
  digitalWrite(motorDirectionPin1, HIGH);
  digitalWrite(motorDirectionPin2, LOW);
}

void stopConveyor() {
  conveyorRunning = false;
  analogWrite(motorSpeedPin, 0);
  digitalWrite(motorDirectionPin1, LOW);
  digitalWrite(motorDirectionPin2, LOW);
}

void loop() {
  // Maintain conveyor state
  if (conveyorRunning) {
    analogWrite(motorSpeedPin, motorSpeed);
    digitalWrite(motorDirectionPin1, HIGH);
    digitalWrite(motorDirectionPin2, LOW);
  }
  
  // Check for serial commands
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    switch (command) {
      case 'S':  // Stop conveyor
        stopConveyor();
        Serial.println("STOPPED");
        break;
        
      case 'G':  // Go (start conveyor)
        startConveyor();
        Serial.println("RUNNING");
        break;
        
      case 'W':  // West
        sortingServo.write(WEST_POSITION);
        delay(MOVE_DELAY);
        sortingServo.write(CENTER_POSITION);
        delay(MOVE_DELAY);
        Serial.println("OK");
        break;
        
      case 'E':  // East
        sortingServo.write(EAST_POSITION);
        delay(MOVE_DELAY);
        sortingServo.write(CENTER_POSITION);
        delay(MOVE_DELAY);
        Serial.println("OK");
        break;
        
      case 'C':  // Center
        sortingServo.write(CENTER_POSITION);
        Serial.println("OK");
        break;
        
      default:
        Serial.println("ERR");
        break;
    }
  }
}
