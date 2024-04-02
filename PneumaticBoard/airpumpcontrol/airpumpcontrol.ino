int POTpin = A15;
int solenoidPin = 12;
int solenoidPin1 = 11;
int solenoidPin2 = 10;
int solenoidPin3 = 9;
int POTval, mapval; 

struct SolVals {
  int open;
  int closed;
};

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(solenoidPin, OUTPUT);
  pinMode(solenoidPin1, OUTPUT); //sets pin as output
  pinMode(solenoidPin2, OUTPUT);
  pinMode(solenoidPin3, OUTPUT);
}

void loop() {
  POTval = analogRead(POTpin);
  mapval = map(POTval, 0, 1023, 0, 100);
  
  // Call getTwoValues to initialize result with the current mapval
  SolVals result = getTwoValues(mapval);
  
  // POTval and mapval for debugging
  Serial.print("POTval: ");
  Serial.print(POTval);
  Serial.print("\tMapval: ");
  Serial.println(mapval);
  Serial.println();
  // Open and Closed
  Serial.print("Open: ");
  Serial.print(result.open);
  Serial.print("\tClosed: ");
  Serial.println(result.closed);
  
  if (mapval >= 65) {
    digitalWrite(solenoidPin, 255);
    digitalWrite(solenoidPin1, 255);
    digitalWrite(solenoidPin2, 255);
    digitalWrite(solenoidPin3, 255);
    Serial.println("Here");
  } else {
    // Use the result to control the solenoid
    digitalWrite(solenoidPin1, 255); // Turn on solenoid.
    digitalWrite(solenoidPin, 255); // Turn on solenoid.
    digitalWrite(solenoidPin2, 255);
    digitalWrite(solenoidPin3, 255);
    //delay(1000); For debuggin purposes.
    delay(result.open); // Delay for the time it should be open
    digitalWrite(solenoidPin1, 0); // Turn off solenoid.
    digitalWrite(solenoidPin, 0); // Turn off solenoid.
    digitalWrite(solenoidPin2, 0);
    digitalWrite(solenoidPin3, 0);
    //delay(1000); For debbuging purposes. 
    delay(result.closed); // Delay for the time it should be closed.
  }  
}

SolVals getTwoValues(int val) {
  SolVals result;
  // Maps 0% - 100% to the amount of time it should be open in milliseconds. 
  int time = map(val, 0, 100, 0, 15);
  // the amount of time it stays Open.
  result.open = time;
  // The amount of time it stays close.
  result.closed = 15 - time;
  return result;
}