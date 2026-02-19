#include <IRremote.hpp> // Note the .hpp - recommended for 4.5.0+

const int RECV_PIN = 11;
int motor1pin1 = 2;
int motor1pin2 = 3;
bool motorOn = false;
int motorSpeed = 100;
int motorEnable = 9;
int motorIncrement = 50;
int motorThresh[] = {1, 250};
int potVal = analogRead()


void setup() {
  pinMode(motor1pin1, OUTPUT);
  pinMode(motor1pin2, OUTPUT);
  Serial.begin(9600);
  delay(2000); // 2-second buffer to prevent "Square" characters
  Serial.println(F("STARTING IR RECEIVER..."));
  // Start the receiver
  IrReceiver.begin(RECV_PIN, ENABLE_LED_FEEDBACK);
}

void loop() {
  if (IrReceiver.decode()) {
    //Print a summary of what was received
    IrReceiver.printIRResultShort(&Serial);
    
    //Specifically print the HEX code like you wanted
    uint32_t recCode = IrReceiver.decodedIRData.decodedRawData;
    // Power
    if (recCode == 0xBA45FF00){
      if (!motorOn) {
        digitalWrite(motor1pin1, HIGH);
        digitalWrite(motor1pin2, LOW);
        analogWrite(motorEnable,motorSpeed);
        Serial.println(motorSpeed);
        motorOn = true;
      }
      else {
        digitalWrite(motor1pin1, LOW);
        motorOn = false;
      }
      // Up button speed 0xF609FF00
      
      // Down button speed 
    }
    // For motor speed under camera  slow it down
    if (recCode == 0xF609FF00){
      if (motorOn){
        Serial.println(F("Speeding Up"));
        motorSpeed+=motorIncrement;
        if (motorSpeed <= motorThresh[1]){
          motorSpeed=motorThresh[1];
        }
        Serial.println(motorSpeed);
        analogWrite(motorEnable,motorSpeed);
      }
    }
    if (recCode == 0xF807FF00){
      if (motorOn){
        Serial.println(F("Slowing down"));
        motorSpeed-=motorIncrement;
        if (motorSpeed >= motorThresh[0]){
          motorSpeed=motorThresh[0];
        }
        Serial.println(motorSpeed);
        analogWrite(motorEnable,motorSpeed);
      }
    }
    IrReceiver.resume(); // Enable receiving of the next value
  }
  // digitalWrite(motor1pin1, HIGH);
  // digitalWrite(motor1pin2, LOW);
  // Serial.println("Motor Started for 5 seconds");
  //delay(1000);
  //digitalWrite(motor1pin1, LOW);
  //Serial.println("Motor Stopped.");
}