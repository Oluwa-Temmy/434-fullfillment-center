// DC motor control code for Arduino 
// Code was complied and uploaded onto Arduino board via the Arduino IDE software

// Pin definitions for our Arduino board
int motorSpeedPin = 3;
int motorDirectionPin1 = 4;
int motorDirectionPin2 = 5;

// Setup function to initialize the motor control pins
void setup() {
pinMode(motorSpeedPin, OUTPUT);
pinMode(motorDirectionPin1, OUTPUT);
pinMode(motorDirectionPin2, OUTPUT);
}

// Loop function to control the motor speed and direction
// Set the motor speed to 100 (out of 255) and direction to forward
void loop() {
analogWrite(motorSpeedPin, 100);
digitalWrite(motorDirectionPin1, HIGH);
digitalWrite(motorDirectionPin2, LOW);
}