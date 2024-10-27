//New version of airpumpcontrol for more accurate air flow control
//Christian Diaz Herrera 10/4/2024

int POTpin1 = A15;
// int POTpin2 = A14;
int solenoidPin1 = 2;
int solenoidPin2 = 3;
int solenoidPin3 = 4;
int solenoidPin4 = 5;

int POTval1, mapval1;
// int POTval2, mapval2;



void setup() {
  Serial.begin(9600);
  pinMode(solenoidPin1, OUTPUT);
  pinMode(solenoidPin2, OUTPUT);
  pinMode(solenoidPin3, OUTPUT);
  pinMode(solenoidPin4, OUTPUT);
}

void loop() {
  POTval1 = analogRead(POTpin1);
  mapval1 = map(POTval1, 0, 1023, 0,255);
  // POTval2 = analogRead(POTpin2);
  // mapval2 = map(POTval2, 0, 1023, 0, 255);

  Serial.print("POTval1: ");
  Serial.print(POTval1);
  Serial.print("\tMapval1: ");
  Serial.print(mapval1);
  Serial.println();
  // Serial.print("POTval2: " );
  // Serial.print(POTval2);
  // Serial.print("\tMapval2: ");
  // Serial.print(mapval2);
  // Serial.println();

  analogWrite(solenoidPin1, mapval1);
  // delay(100);
  analogWrite(solenoidPin2, mapval1);
  analogWrite(solenoidPin3, mapval1);
  analogWrite(solenoidPin4, mapval1);
}
