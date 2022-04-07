#include "HX711.h"

// define pins for switch and load cell
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;
const int switchPin = 7;

// define calibration constants
const float slopeValue = 0.0022333; //5kg load cell, upside down
const float offsetValue = 95; //5kg load cell, upside down

//10kg load cell, arrow pointed down
/*Slope
-0.0045769
offest
-592*/

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
  
  Serial.begin(9600); //begin serial port to communicate with laptop
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN); //begin the scale
  Serial.println("Began scale.");
  delay(500);

  readDelayStart = millis();
  getDataDelayStart = millis();

}

void loop() {
  currentTs = millis();
  
  if((currentTs - readDelayStart) > readDelayNum){
     //Serial.println("inside READ delay");
     recvWithStartEndMarkers();
     showNewData();
     readDelayStart = millis();
   }

  //if we have recieved the GETDATA command from the laptop
  if(sendTelem){
    if((currentTs - getDataDelayStart) > getDataDelayNum){
        //make sure to grab data from the sensor until it has data
        int gotValue = 0; //we have not gotten data yet
        long reading; 
         while(!gotValue){ //while we have not gotten data
          //if the scale is ready, grab the data 
          if (scale.is_ready()) { 
            reading = scale.read(); //grab load cell reading
            gotValue = 1; //set gotValue to 1 because we do have data
          }else{
            Serial.println("Couldn't get data"); //print that scale not ready data
          }
         }
        //grab current time and calculate the weight from the raw load cell reading
        unsigned long currentTime = millis();
        //calculate weight based on calibrated slope and offset values
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
    //as long we are not currently reading a message and there 
    //is serial data available, keeping grabbing the next character on the serial port
    while (Serial.available() > 0 && newData == false) { 
        rc = Serial.read();
        if (recvInProgress == true) { //if we are currently reading a message
            //if we have not reached the end of the message, keep reading characters
            if (rc != endMarker) { 
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            //if we have reached the end of the message, set the recvInProgress flag 
            //back to false, set newData to true so that the showNewData function 
            //will parse the commands
            else { 
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }
        else if (rc == startMarker) { //if we recieved the first character of a message
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
