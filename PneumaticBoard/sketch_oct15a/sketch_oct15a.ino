
int solenoidPin = 4; //output pin on the arduino board

struct SolVals {
  int open;
  int closed;
};



void setup() {
  // put your setup code here, to run once:

pinMode(solenoidPin, OUTPUT); //sets pin as output
}

//write a function that makes it controllaby high or low, input pow being percentage you want solenoid to close the valve


void loop() {
  // analogWrite(solenoidPin, 191);
  // put your main code here, to run repeatedly:
SolVals result = getTwoValues(90);


analogWrite(solenoidPin, 255);
delay(result.closed);
analogWrite(solenoidPin, 0);
delay(result.open);
// delay(1000); //wait 1 sec
// digitalWrite(solenoidPin, LOW); //switch it to OF`F
// delay(1000); //wait 1 sec
// analogWrite(solenoidPin, 260);
}


SolVals getTwoValues(int pow) {
  SolVals result;
  result.closed = pow*10;
  result.open = 1000 - result.closed;
  return result;
}
