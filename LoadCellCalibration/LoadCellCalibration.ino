//small breadboard - 40g
//michaela phone - 203 g
//tyler phone - 220 g
//caliper + box - 406 g

#include "HX711.h"

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 2;
long calArray[100];
long totalCal = 0;
long offsetValue;
const int calDataPoints = 200;
float weightInputs[6];
long associatedReadings[6];
long singleReadingSum = 0;
float slopeValue;

HX711 scale;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50000000);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);

  delay(500);

  Serial.println("Press Enter when there is nothing on the scale and ready to calibrate");
  while(Serial.available() == 0){}
  Serial.read();

  Serial.println("Calibrating...");

   for(int i = 0; i < calDataPoints; i++){
    if (scale.is_ready()) {
      long reading = scale.read();
      //Serial.print("HX711 reading: ");
      Serial.println(i);
      calArray[i] = reading;
      totalCal += reading;
    } else {
      Serial.println("HX711 not found.");
      Serial.println(i);
      i--;
    }

    delay(13);
  }

  offsetValue = totalCal / (long int)calDataPoints;

  Serial.println("Offset value: ");
  Serial.println(offsetValue);


  for(int i=0; i <= 5; i++){
    Serial.println("Write Weight [g]: ");
    while(Serial.available() == 0){}
    weightInputs[i] = Serial.parseFloat();
    Serial.println(weightInputs[i], 4);

  for(int i = 0; i < 10; i++){
    
    int gotValue = 0;
    while(!gotValue){
      if (scale.is_ready()) {
        long reading = scale.read();
        singleReadingSum += reading;
        gotValue = 1;
      }
    }

    delay(30);
    
  }
 
  associatedReadings[i] = long(float(singleReadingSum) / 10);
  Serial.println(associatedReadings[i]);

  singleReadingSum = 0;
   
 
  }

  Serial.println("Weights and Readings");
  for(int i = 0; i<=5; i++){
    Serial.print(weightInputs[i]);
    Serial.print(" ");
    Serial.println(associatedReadings[i]);
  }

  float slope1 = (float)(weightInputs[1] - weightInputs[0]) / (float)(associatedReadings[1] - associatedReadings[0]);
  float slope2 = (float)(weightInputs[2] - weightInputs[1]) / (float)(associatedReadings[2] - associatedReadings[1]);
  float slope3 = (float)(weightInputs[3] - weightInputs[2]) / (float)(associatedReadings[3] - associatedReadings[2]);
  float slope4 = (float)(weightInputs[4] - weightInputs[3]) / (float)(associatedReadings[4] - associatedReadings[3]);
  float slope5 = (float)(weightInputs[5] - weightInputs[4]) / (float)(associatedReadings[5] - associatedReadings[4]);

  Serial.println(slope1, 7);
  Serial.println(slope2, 7);
  Serial.println(slope3, 7);
  Serial.println(slope4, 7);
  Serial.println(slope5, 7);

  slopeValue  = (slope1 + slope2 + slope3 + slope4 + slope5) / 5;
  offsetValue = -1 * (offsetValue * slopeValue);

  Serial.println("Slope");
  Serial.println(slopeValue, 7);
  Serial.println("offest");
  Serial.println(offsetValue);
  
  
}

void loop() {

  Serial.println("Place an item on the scale. Hit Enter when ready");
  while(Serial.available() == 0){}
  Serial.read();
  
  //Serial.println(slopeValue);
  //Serial.println(offsetValue);

  long weightReadingSum = 0;

  for(int i = 0; i < 10; i++){
    
    int gotValue = 0;
    while(!gotValue){
      if (scale.is_ready()) {
        long reading = scale.read();
        weightReadingSum += reading;
        gotValue = 1;
      }
    }

    delay(30);
    
  }

  long actualWeightReading = long(float(weightReadingSum) / 10);

  float weight = (float)actualWeightReading * slopeValue + (float)offsetValue;

  Serial.println(weight);
  
  
 

  //delay(1000);
  
}
