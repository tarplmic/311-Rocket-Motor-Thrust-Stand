#include "HX711.h"

// define pins for switch and load cell
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;
const int switchPin = 7;

// define calibration constants
const float slopeValue = -0.003;
const float offsetValue = 360;

const long readDelayNum = 100;
long readDelayStart; 
const long getDataDelayNum = 12;
long getDataDelayStart;

bool sendTelem = false;

const byte numChars = 40;
char receivedChars[numChars];
boolean newData = false;
unsigned long currentTs;

void recvWithStartEndMarkers();
void showNewData();

// create a new scale instance
HX711 scale;

void setup() {
  // begin serial port, initialize load cell, and set switch pin as an input
  
  Serial.begin(9600);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  Serial.println("Began scale.");
  pinMode(switchPin, INPUT);
  delay(500);

  readDelayStart = millis();
  getDataDelayStart = millis();

}

void loop() {

  //check the state of the switchPin
  //int buttonState = digitalRead(switchPin);
  currentTs = millis();

  if((currentTs - readDelayStart) > readDelayNum){
     //Serial.println("inside READ delay");
     recvWithStartEndMarkers();
     showNewData();
     readDelayStart = millis();
   }

  //if the button is 0, connected to gnd
  if(sendTelem){
   
    if((currentTs - getDataDelayStart) > getDataDelayNum){
        //Serial.println("inside GETDATA delay");
  
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
        //delay(12); 
    
        //grab current time and calculate the weight from the raw load cell reading
        unsigned long currentTime = millis();
        float weight = (float)reading * slopeValue + (float)offsetValue;
    
        //send data over serial port
        Serial.println("d," + String(weight) + "," + String(currentTime));
      
  
      getDataDelayStart = millis();
    }
  }
 

}


void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
    
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void showNewData() {
  if (newData == true) {
    String stringVersionReceivedChars;
    stringVersionReceivedChars = receivedChars;

    if (stringVersionReceivedChars == "CMD,GETDATA"){
        sendTelem = true;
        Serial.println("RECIEVEED DATA ON");
        
     }else if (stringVersionReceivedChars == "CMD,STOPDATA"){
        sendTelem = false;
        Serial.println(sendTelem);
        Serial.println("RECIEVEED DATA OFF");
     }
    
    newData = false;
    }
}
