int POTpin = A0;
int solenoidPin = 4;
int solenoidPin1 = 3;
int POTval, mapval; //output pin on the arduino board

struct SolVals {
  int open;
  int closed;
};



void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
pinMode(solenoidPin, OUTPUT);
pinMode(solenoidPin1, OUTPUT); //sets pin as output
}

//write a function that makes it controllaby high or low, input pow being percentage you want solenoid to close the valve


void loop() {
  POTval = analogRead(POTpin);
  Serial.print(POTval) ;
  mapval = map(POTval, 0, 1023, 0, 100);
  Serial.print("\t");
  Serial.println(mapval);
SolVals result = getTwoValues(mapval);





analogWrite(solenoidPin, 255);
analogWrite(solenoidPin1, 255);
delay(result.closed);
analogWrite(solenoidPin, 0);
analogWrite(solenoidPin1, 0);
delay(result.open);

// if (mapval = 100) {
//     analogWrite(solenoidPin, 255);
//     analogWrite(solenoidPin1, 255);
//   } else if (mapval = 0){
//     analogWrite(solenoidPin, 0);
//     analogWrite(solenoidPin1, 0);
//   } else {
//     analogWrite(solenoidPin, 255);
//     analogWrite(solenoidPin1, 255);
//     delay(result.closed);
//     analogWrite(solenoidPin, 0);
//     analogWrite(solenoidPin1, 0);
//     delay(result.open);
//   }

}


SolVals getTwoValues(int pow) {
  SolVals result;
  result.closed = pow/15;
  result.open = 15 - result.closed;
  return result;
}
