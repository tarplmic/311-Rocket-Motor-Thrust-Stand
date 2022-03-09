int whiteWire = A0;
int greenWire = A2;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  int val1 = analogRead(whiteWire);
  int val2 = analogRead(greenWire);

  Serial.print("Val1: ");
  Serial.println(val1);
  //Serial.print("Val2: ");
  //Serial.println(val2);

  delay(1000);

}
