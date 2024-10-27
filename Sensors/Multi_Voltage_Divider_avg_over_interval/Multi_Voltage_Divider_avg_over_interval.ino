

/*===========================================================     Header     ==============================================================

  Katelyn Rosethorn M.
  Created: Monday, October 2nd
  Updated: Monday, October 9th

  Reading from a voltage divider, sums the last n (interval) voltage measurements from each pin, and,
  after every interval of n measurements, calculates and prints the resistances for each sensor

/*========================================================   Define Constants   ==========================================================*/

const int interval = 2000;              // make n = interval measurements before calculating the average and printing
const int resistor_known = 1000;        // Known resistor in the voltage divider. See circuit diagram in README
const int voltage_in = 5;               // 5V voltage_in
const float sensor_to_5V = 5.0 / 1023;  //scalar to scale analogRead output to 0 to 5V scale

/*================================================   Initialization and Sensor Setup   ===================================================*/


typedef struct Sensor {
  /*
    Description: 
      Sensors are stored as "structs", with editible inputs name and pin.
    Variables:
      char *name: Sensor's name
      int pin:    Arduino pin the resistance is read from, ie Vout
      float voltage_um: value used to hold the sum over n measurements
      float resistance: holds the resistance of the sensor; updated every n measurements
  */
  char *name;
  int pin;
  float voltage_sum = 0.0;
  float resistance = 0.0;
};

/*
*   Procedure for adding a new sensor:
*   i)   Update number_of_sensors:                    this should match the number of sensors connected. Counts up starting at 1.
*   ii)  Assign a name and pin to the new sensor:     let j be as in adding the jth sensor. Then we'd define its values as follows:
*             Sensors[j].name = "Sensor Aj";
*             Sensors[j].pin = Aj;
*/

const int number_of_sensors = 2;
Sensor Sensors[number_of_sensors];
void setup() {
  Serial.begin(9600);

  Sensors[0].name = "Sensor A0";
  Sensors[0].pin = A0;

  Sensors[1].name = "Sensor A1";
  Sensors[1].pin = A1;
}

/*=============================================================   Loop   ====================================================================*/

float calc_average (float sum, int interval){
  /*
  Description:
    returns the average of sum assuming interval elements summed
  Args:
    float sum:          sum over all elements
    int   interval:     the number of elements
  Returns:
    float:              sum / interval
  */
  return sum / float(interval);
}

float update_voltage_sum(int sensor_reading, float voltage_sum){
  /*
  Description:
    returns the updated voltage_sum, given a sensor_reading
  Args:
    int sensor_reading: reading from a sensor
    float  voltage_sum: the current voltage sum for a sensor
  Returns:
    float:               sensor reading converted to voltage + previous sum
  */
  float voltage_out = float(sensor_reading) * sensor_to_5V;
  return (voltage_sum + voltage_out);
}

float calc_resistance_from_voltage_sum(float voltage_sum){
  /*
  Description:
    Given the sum of the voltage over interval, calculates the average voltage, calculates the unknown resistance, and returns it
  Args:
    float        voltage_sum: the sum of voltages over interval measurements
  Returns:
    float unknown_resistance: the resistance of the voltage divider's unknown load
  */
  float voltage_over_R_unknown = calc_average(voltage_sum, interval);
  float unknown_resistance = voltage_over_R_unknown * resistor_known / (voltage_in - voltage_over_R_unknown);
  return unknown_resistance;
}

void loop() {

  int measurements = 0;
  // for each sensor, update the sum given the pin reading and previous sum
  for (int i = 0; i < number_of_sensors; i++){
    Sensors[i].voltage_sum = update_voltage_sum(analogRead(Sensors[i].pin), Sensors[i].voltage_sum);
  }
  measurements++;

  // When an interval is completed, for each sensor, the resistance is calculated from the voltage sum and printed, and the sum is reset to 0.
  if (measurements % interval == 0){
    Serial.println("========================================================================");
    for (int i = 0; i < number_of_sensors; i++){
      Sensors[i].resistance = calc_resistance_from_voltage_sum(Sensors[i].voltage_sum);
      Serial.println(String(Sensors[i].name) + " has resistance " + String(Sensors[i].resistance));
      Sensors[i].voltage_sum = 0;
    }

  }  

}

