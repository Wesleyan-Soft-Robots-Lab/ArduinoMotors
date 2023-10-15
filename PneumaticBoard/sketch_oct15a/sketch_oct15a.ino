
int solenoidPin = 4; //output pin on the arduino board



void setup() {
  // put your setup code here, to run once:
pinMode(solenoidPin, OUTPUT); //sets pin as output
}

void loop() {
  // put your main code here, to run repeatedly:
digitalWrite(solenoidPin, HIGH); //switches solenoid to ON
delay(1000); //wait 1 sec
digitalWrite(solenoidPin, LOW); //switch it to OFF
delay(1000); //wait 1 sec
}
