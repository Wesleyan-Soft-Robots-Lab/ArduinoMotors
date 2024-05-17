// Code by Christian Diaz Herrera and Kevin Angulo Lezama

//This is the most recent version of the pneumatic board control. This allows for individual control of the dials and thus pairs of air valves. - Kevin Angulo Lezama

int POTpin1 = A15;
int POTpin2 = A14;
int solenoidPin1 = 1;
int solenoidPin2 = 2;
int solenoidPin3 = 3;
int solenoidPin4 = 4;
int POTval1, POTval2, mapval1, mapval2; 

struct SolVals {
  int open;
  int closed;
};

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(solenoidPin1, OUTPUT);
  pinMode(solenoidPin2, OUTPUT); //sets pin as output
  pinMode(solenoidPin3, OUTPUT);
  pinMode(solenoidPin4, OUTPUT);
}

void loop() {

  // Getting the values from both dials
  POTval1 = analogRead(POTpin1);
  mapval1 = map(POTval1, 0, 1023, 0, 100);
  
  POTval2 = analogRead(POTpin2);
  mapval2 = map(POTval2, 0, 1023, 0, 100);
  
  // Call getTwoValues to initialize result with the current mapval
  SolVals result1 = getTwoValues(mapval1);
  SolVals result2 = getTwoValues(mapval2);
  
  // POTval and mapval for debugging
  Serial.print("POTval1: ");
  Serial.print(POTval1);
  Serial.print("\tMapval1: ");
  Serial.println(mapval1);
  Serial.println();
  Serial.print("POTval2: ");
  Serial.print(POTval2);
  Serial.print("\tMapval2: ");
  Serial.println(mapval2);
  Serial.println();
  
  // Open and Closed
  Serial.print("Open1: ");
  Serial.print(result1.open);
  Serial.print("\tClosed1: ");
  Serial.println(result1.closed);
  Serial.println();
  Serial.print("Open2: ");
  Serial.print(result2.open);
  Serial.print("\tClosed2: ");
  Serial.println(result2.closed);
  Serial.println();
  
  if (mapval1 >= 70) {
    digitalWrite(solenoidPin1, HIGH); // Turn on solenoid.
    digitalWrite(solenoidPin2, HIGH); // Turn on solenoid.
    Serial.println("Solenoid 1 & 2 Here");
  } else if (mapval1 <= 5){
    digitalWrite(solenoidPin1, LOW); // Turn off solenoid.
    digitalWrite(solenoidPin2, LOW); // Turn off solenoid.
  } else {
    // Use the result to control the solenoid
    digitalWrite(solenoidPin1, HIGH); 
    digitalWrite(solenoidPin2, HIGH); 
    delay(result1.open); // Delay for the time it should be open
    digitalWrite(solenoidPin1, LOW); 
    digitalWrite(solenoidPin2, LOW);
    delay(result1.closed); // Delay for the time it should be closed.
  }  

  if (mapval2 >= 70) {
    digitalWrite(solenoidPin3, HIGH); // Turn on solenoid.
    digitalWrite(solenoidPin4, HIGH); // Turn on solenoid.
    Serial.println("Solenoid 3 & 4 Here");
  } else if (mapval2 <= 5){
    digitalWrite(solenoidPin3, LOW); // Turn off solenoid.
    digitalWrite(solenoidPin4, LOW); // Turn off solenoid.
  } else {
    // Use the result to control the solenoid
    digitalWrite(solenoidPin3, HIGH);
    digitalWrite(solenoidPin4, HIGH);
    delay(result2.open); // Delay for the time it should be open
    digitalWrite(solenoidPin3, LOW);
    digitalWrite(solenoidPin4, LOW);
    delay(result2.closed); // Delay for the time it should be closed.
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
