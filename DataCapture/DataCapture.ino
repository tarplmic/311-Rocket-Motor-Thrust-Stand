#include "HX711.h"

// define pins for switch and load cell
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;
const int switchPin = 7;

// define calibration constants
const float slopeValue = -0.003;
const float offsetValue = 360;

// create a new scale instance
HX711 scale;

void setup() {
  // begin serial port, initialize load cell, and set switch pin as an input
  
  Serial.begin(9600);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  Serial.println("Began scale.");
  pinMode(switchPin, INPUT);
  delay(500);

}

void loop() {

  //check the state of the switchPin
  int buttonState = digitalRead(switchPin);

  //if the button is 0, connected to gnd
  if(!buttonState){ 

    //make sure to grab data from the sensor until it has data
    int gotValue = 0;
    long reading; 

     while(!gotValue){
      //if the scale is ready, grab the data 
      if (scale.is_ready()) {
        reading = scale.read();
        gotValue = 1;
      }else{
        Serial.println("Couldn't get data");
      }
    }

    //appropriate wait time is around 13 ms, but it takes time to check button and write to serial so we can wait less than 13
    delay(12); 

    //grab current time and calculate the weight from the raw load cell reading
    unsigned long currentTime = millis();
    float weight = (float)reading * slopeValue + (float)offsetValue;

    //send data over serial port
    Serial.println("d," + String(weight) + "," + String(currentTime));
  }
 

}
