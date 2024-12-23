
#include <List.hpp>
/*===========================================================     Header     ==============================================================

  Katelyn Rosethorn M.
  Created: Monday, October 9th
  Updated: Thursday, October 12th

  This file serves to reduce the voltage-divider reading sketches to a setup that can more easily output to motors with an update_sensors() and get_resistance() function

  Instructions:
    - To add a sensor, update number_of_sensors on line 40 and add it in a similar fashion to others in Sensor_Init()

/*=========================================================   Device Setup   =============================================================*/


const int MAX_WINDOW_SIZE = 15;         // the size of the moving window of voltages we are reading from the sensor
const int voltage_in = 5;               // 5V voltage_in
const float sensor_to_5V = 5.0 / 1023;  //scalar to scale analogRead output to 0 to 5V scale

int POTpin1 = A5; //The following two pins are for reading the potentiometer readings to control arm for now
int POTpin2 = A6;
int solenoidPin1 = 2; //The following 4 pins are for the power of which we control the solenoids
int solenoidPin2 = 3;
int solenoidPin3 = 4;
int solenoidPin4 = 5;

int POTval1, mapval1, percent1; //These values will be converted to percentages and mapped to the right values for controlling solenoids
int POTval2, mapval2, percent2;

typedef struct Sensor {
  /*
    Description: 
      Sensors are stored as "structs", with editible inputs name and pin.
    Variables:
      *name: char array                 Sensor's name
      pin: int                          Arduino pin the resistance is read from, ie Vout
      voltage_window: List <float>      window used to store voltages
      voltage_sum: float                value used to hold the sum over n measurements
      resistance: float                 holds the resistance of the sensor; updated every n measurements
  */
  char *name = "";
  int pin = A0;
  float resistor_known = 90; //ohms
  List<float> voltage_window;
  float voltage_sum = 0;
  float resistance = 0.0;
};

const int number_of_sensors = 4;
Sensor Sensors[number_of_sensors];
void Sensor_Init() {
  Sensors[0].name = "Sensor 1";
  Sensors[0].pin = A0;
  Sensors[0].resistor_known = 90.05;

  Sensors[1].name = "Sensor 3";
  Sensors[1].pin = A1;
  Sensors[1].resistor_known = 90.05;

  Sensors[2].name = "Sensor 5";
  Sensors[2].pin = A2;
  Sensors[2].resistor_known = 90.05;

  Sensors[3].name = "Sensor 7";
  Sensors[3].pin = A3;
  Sensors[3].resistor_known = 90.08;

  calibrate_devices();
}

/*=========================================================   Helper Functions   ===========================================================*/

bool calibrated = false; // true if calibration has been run

float get_voltage(int pin){
  /**
  Description:
    Returns the voltage from the given pin
  Arguments:
    @param pin: int        the pin to read voltage from
  Returns:
    @return :float         the voltage from given pin
  */
  return analogRead(pin) * sensor_to_5V;
}

float calc_resistance(float voltage_out, float resistor_known) {
  /**
  Description:
    Returns the resistance, calculated from Vout of the corresponding pin
  Arguments:
    @param voltage_out: float         voltage read from a sensor
    @param resistor_known: float      known resistor in the sensor
  Returns:
    @return resistance: float         resistance calculated from V_out
  */
  float resistance = 0;
  resistance = (voltage_out*resistor_known) / (voltage_in - voltage_out);
  return resistance;
}

int measurements = 0;
void update_sensors() {
  /*
  Description:
    Should be called every loop iteration for ideal measurements. Updates the sensors' voltage_window and voltage_sum
    and calls calc_resistance() if the sensors have been calibrated
  */
  for(int i=0; i < number_of_sensors; i++) {
    float voltage = get_voltage(Sensors[i].pin);
    Sensors[i].voltage_window.add(voltage);
    Sensors[i].voltage_sum += voltage;
    if (calibrated) {
      Sensors[i].voltage_sum -= Sensors[i].voltage_window[0];
      Sensors[i].voltage_window.removeFirst();
      Sensors[i].resistance = calc_resistance(Sensors[i].voltage_sum / MAX_WINDOW_SIZE, Sensors[i].resistor_known);
      // Sensors[i].resistance = voltage;
    }
  }
}

String debug(){
  /**
  Description:
    returns a column-formatted string of the sensor resistance values
  */
  long t = millis();
  String debug_string = String(t);
  for (int i=0; i < number_of_sensors; i++) {
    debug_string = debug_string + " " + String(Sensors[i].resistance);
  }
  return debug_string;
}

/*=============================================================   Initialization  ========================================================*/

void calibrate_sensors() {
  for (int i=0; i < MAX_WINDOW_SIZE; i++){
    update_sensors();
  }
}

void calibrate_devices() {
  calibrate_sensors();
  calibrated = true;
}

void setup() {
  Serial.begin(9600);
  Sensor_Init();
}

/*=============================================================   Loop   ====================================================================*/

void loop() {

  /* Get sensor readings and print them */
  update_sensors();
  Serial.print("Resistance: ");
  Serial.print(debug());

  /* Desired position */
  // POTval1 = analogRead(POTpin1);
  // mapval1 = map(POTval1, 0, 1023, 0,255);
  // percent1 = map(POTval1, 0, 1023, 0,100);
  // POTval2 = analogRead(POTpin2);
  // mapval2 = map(POTval2, 0, 1023, 0, 255);
  // percent2 = map(POTval2, 0,1023, 0,100);
  while (!Serial.available() == 0) {

  }
  String response = Serial.readStringUntil('\n');

  /* */
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

  /* Write to the solenoids */
  analogWrite(solenoidPin1, mapval1);
  // delay(100);
  analogWrite(solenoidPin2, mapval1);
  analogWrite(solenoidPin3, mapval2);
  analogWrite(solenoidPin4, mapval2);
}

