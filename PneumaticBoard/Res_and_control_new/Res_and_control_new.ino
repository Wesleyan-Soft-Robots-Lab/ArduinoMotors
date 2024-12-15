//New version of airpumpcontrol for more accurate air flow control
//Christian Diaz Herrera 10/4/2024

int POTpin1 = A15;
int POTpin2 = A14;
int solenoidPin1 = 2;
int solenoidPin2 = 3;
int solenoidPin3 = 4;
int solenoidPin4 = 5;
int S0 = A0;
int S1 = A1;
int S2 = A2;
int S3 = A3;


int POTval1, mapval1, percent1;
int POTval2, mapval2, percent2;



void setup() {
  Serial.begin(9600);
  pinMode(solenoidPin1, OUTPUT);
  pinMode(solenoidPin2, OUTPUT);
  pinMode(solenoidPin3, OUTPUT);
  pinMode(solenoidPin4, OUTPUT);
  pinMode(S0, INPUT);
  pinMode(S1, INPUT);
  pinMode(S2, INPUT);
  pinMode(S3, INPUT);
}

void loop() {
  POTval1 = analogRead(POTpin1);
  mapval1 = map(POTval1, 0, 1023, 0,255);
  percent1 = map(POTval1, 0, 1023, 0,100);
  POTval2 = analogRead(POTpin2);
  mapval2 = map(POTval2, 0, 1023, 0, 255);
  percent2 = map(POTval2, 0,1023, 0,100);

  Serial.print("Sensor1: ");
  Serial.print(analogRead(S0));
  Serial.print("\tSensor2: ");
  Serial.print(analogRead(S1));
  Serial.print("\tSensor3: ");
  Serial.print(analogRead(S2));
  Serial.print("\tSensor4: ");
  Serial.print(analogRead(S3));

  Serial.print("\tPotval1: ");
  Serial.print(POTval1);
  // Serial.println();
  Serial.print("\tmapval1 ");
  Serial.print(mapval1);
  Serial.print("\tPercentage: ");
  Serial.print(percent1);
  // Serial.println();
  Serial.print("\tPotval2: " );
  Serial.print(POTval2);
  // Serial.println();
  Serial.print("\tmapval2: ");
  Serial.print(mapval2);
  Serial.print("\tPercentage: ");
  Serial.print(percent2);
  Serial.println();

  analogWrite(solenoidPin1, mapval1);
  // delay(100);
  analogWrite(solenoidPin2, mapval1);
  analogWrite(solenoidPin3, mapval2);
  analogWrite(solenoidPin4, mapval2);
}
