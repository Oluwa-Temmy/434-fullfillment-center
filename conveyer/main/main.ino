int motorSpeedPin = 3;
int motorDirectionPin1 = 4;
int motorDirectionPin2 = 5;

void setup() {
pinMode(motorSpeedPin, OUTPUT);
pinMode(motorDirectionPin1, OUTPUT);
pinMode(motorDirectionPin2, OUTPUT);
}

void loop() {
analogWrite(motorSpeedPin, 100);
digitalWrite(motorDirectionPin1, HIGH);
digitalWrite(motorDirectionPin2, LOW);
}