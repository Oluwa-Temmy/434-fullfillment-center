#include <IRremote.hpp>
#include <Servo.h>

const int RECV_PIN = 11;
int motor1pin1 = 9;
int motor1pin2 = 3;
bool motorOn = false;
int motorSpeed = 100;
int motorEnable = 2;
int motorIncrement = 20;
int motorThresh[] = {1, 250};

// servo setup
Servo armServo;
const int SERVO_PIN = 6;

void setup() {
  pinMode(motor1pin1, OUTPUT);
  pinMode(motor1pin2, OUTPUT);

  // servo
  armServo.attach(SERVO_PIN);

  Serial.begin(9600);
  delay(2000);
  Serial.println(F("STARTING IR RECEIVER..."));
  IrReceiver.begin(RECV_PIN, ENABLE_LED_FEEDBACK);
}

void loop() {
  if (IrReceiver.decode()) {
    IrReceiver.printIRResultShort(&Serial);
    
    uint32_t recCode = IrReceiver.decodedIRData.decodedRawData;

    if (recCode == 0xBA45FF00){
      if (!motorOn) {
        turnOnMotor();
        setArmPos();
      } else {
        turnOffMotor();
      }
    }

    if (recCode == 0xF609FF00) {
      if (motorOn) increaseSpeed();
    }

    if (recCode == 0xF807FF00) {
      if (motorOn) decreaseSpeed();
    }

    if (recCode == 0xE916FF00){
      sendToWest();
    } else if (recCode == 0xF30CFF00){
      sendToEast();
    } else {
      sendToUnprocessed();
    }

    IrReceiver.resume();
  }
}

void turnOnMotor(){
  digitalWrite(motor1pin1, HIGH);
  digitalWrite(motor1pin2, LOW);
  analogWrite(motorEnable, motorSpeed);
  Serial.println(motorSpeed);
  motorOn = true;
}

void turnOffMotor(){
  digitalWrite(motor1pin1, LOW);
  motorOn = false;
}

void increaseSpeed(){
  motorSpeed += motorIncrement;
  if (motorSpeed > motorThresh[1]) {
    motorSpeed = motorThresh[1];
  }
  Serial.print(F("Speeding Up: "));
  Serial.println(motorSpeed);
  analogWrite(motorEnable, motorSpeed);
}

void decreaseSpeed(){
  motorSpeed -= motorIncrement;
  if (motorSpeed < motorThresh[0]) {
    motorSpeed = motorThresh[0];
  }
  Serial.print(F("Slowing Down: "));
  Serial.println(motorSpeed);
  analogWrite(motorEnable, motorSpeed);
}

int getSpeed(){
  Serial.print(F("Current Speed: "));
  Serial.println(motorSpeed);
  return motorSpeed;
}

// Note: servo disables pin 9 and 10, so rearrange motor pins
void sendToUnprocessed(){
  // rotate 60 degrees -- straight down
  armServo.write(90);
}
void sendToEast(){
  // rotate 180 degrees -- to the left
  armServo.write(90);
}
void sendToWest(){
  // rotate 90 degrees -- to the right
  armServo.write(270);
}
void setArmPos(){
  // set arm to default position
  armServo.write(0);
}