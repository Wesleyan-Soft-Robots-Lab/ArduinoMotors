
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  // Serial.setTimeout(1);
}

void loop() {
  // put your main code here, to run repeatedly:
  int test_pin = analogRead(A1);
  Serial.print("Sending: ");
  Serial.println(test_pin);
  while (!Serial.available() == 0) {

  }
  String response = Serial.readStringUntil('\n');
  Serial.print("Output: ");
  Serial.println(response);
  // delay(1000);

}
