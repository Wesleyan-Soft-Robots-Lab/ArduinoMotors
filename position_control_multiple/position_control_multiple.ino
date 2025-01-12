
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

//int POTpin1 = A5; //The following two pins are for reading the potentiometer readings to control arm for now
//int POTpin2 = A6;
int solenoidPin1 = 2; //The following 4 pins are for the power of which we control the solenoids
int solenoidPin2 = 3;
int solenoidPin3 = 4;
int solenoidPin4 = 5;
int S0 = A0;
int S1 = A1;
int S2 = A2;
int S3 = A3;


int solenoid_command0 = 255/2;
int solenoid_command1 = 255/2;

float desired_position0;
float desired_position1;
float position_error0;
float sensed_position0;
float position_error1;
float sensed_position1;
float desired_position00 = -4.0;
float desired_position01 = 25.0;
float desired_position10 = 25.0;
float desired_position11 = 25.0;
float desired_position20 = 0.0;
float desired_position21 = 25.0;
float desired_position30 = -4.0;
float desired_position31 = 0.0;

float last_position0;
float last_position1;

float d_position0;
float d_position1;

float dt;

unsigned long last_millis;
unsigned long current_millis;

int minimum_solenoid_value = 10;

float p_gain = 3.0;
float d_gain = 0.02;

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

/* Take in a string in format [2.343, 16.024392] and return the position as a float */
float get_sensed_position(String response, int which_position) {
  char input[response.length() + 1];
  response.toCharArray(input, sizeof(input));
  float values[2];
  char *bracketStart = strchr(input, '[');
  char *bracketEnd = strchr(input, ']');
  if (bracketStart && bracketEnd) {
    *bracketEnd = '\0';
    bracketStart = bracketStart + 1;
  } else {
    return ;
  }

  char *token = strtok(bracketStart, " ");
  int index = 0;
  while (token != NULL && index < 2) {
    values[index++] = atof(token);
    token = strtok(NULL, " ");
  }
  
  return values[which_position];
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
  analogWrite(solenoidPin1, solenoid_command0);
  analogWrite(solenoidPin2, solenoid_command0);
  analogWrite(solenoidPin3, solenoid_command1);
  analogWrite(solenoidPin4, solenoid_command1);

  // delay(10000);
  
  for(int i = 0; i < 41; i = i + 1) {
    /* Get sensor readings */
    update_sensors();

    /* Send sensor readings to the Python script running on the computer */
    Serial.print(debug());
    Serial.println();

  }

  /* Turn sensor readings into position readings using LSTM model on computer */
  while (!Serial.available() == 0) {
    
  }
  String response = Serial.readStringUntil('\n');
  
  /* We will determine sensed_position0 and sensed_position0 from response with a function */
  sensed_position0 = get_sensed_position(response, 0);
  sensed_position1 = get_sensed_position(response, 1);

}

/*=============================================================   Loop   ====================================================================*/

void loop() {

  last_position0 = sensed_position0;
  last_position1 = sensed_position1;

  last_millis = current_millis;
  current_millis = millis();

  if (current_millis < 20000) {
    desired_position0 = desired_position00;
    desired_position1 = desired_position01;
  } else if (current_millis > 20000 && current_millis < 40000) {
    desired_position0 = desired_position10;
    desired_position1 = desired_position11;
  } else if (current_millis > 40000 && current_millis < 60000) {
    desired_position0 = desired_position20;
    desired_position1 = desired_position21;
  } else {
    desired_position0 = desired_position30;
    desired_position1 = desired_position31;
  }


  dt = float((current_millis - last_millis)/1000);

  /* Get sensor readings */
  update_sensors();

  /* Send sensor readings to the Python script running on the computer */
  Serial.print(debug());
  Serial.println();

  /* Turn sensor readings into position readings using LSTM model on computer */
  while (!Serial.available() == 0) {
    
  }
  String response = Serial.readStringUntil('\n');

  sensed_position0 = get_sensed_position(response, 0);
  sensed_position1 = get_sensed_position(response, 1);
  
  /* Calculate position error and desired position */
  position_error0 = sensed_position0 - desired_position0;
  position_error1 = sensed_position1 - desired_position1;

  /* Calculate error of derivative of position.
     Note: We always want derivative 0 (for this application) so d_position is the same as the error */
  d_position0 = (sensed_position0 - last_position0)/dt;
  d_position1 = (sensed_position1 - last_position1)/dt;

  /* Calculate new command to send to solenoids */
  solenoid_command0 = solenoid_command0 - (int)position_error0*p_gain;
  solenoid_command1 = solenoid_command1 - (int)position_error1*p_gain;

  // Uncomment this and comment out the last two lines if you want to use the derivative gain
  /* 
  solenoid_command0 = solenoid_command0 + (int)(position_error0*p_gain + d_position0*d_gain);
  solenoid_command1 = solenoid_command1 + (int)(position_error1*p_gain + d_position1*d_gain);
  */

  /* Condition the solenoid commands -- keep them within the range [minimum_solenoid_value, 255] */
  if (solenoid_command0 < minimum_solenoid_value) {
    solenoid_command0 = minimum_solenoid_value;
  }
  
  if (solenoid_command1 < minimum_solenoid_value) {
    solenoid_command1 = minimum_solenoid_value;
  }

  if (solenoid_command0 > 255) {
    solenoid_command0 = 255;
  }

  if (solenoid_command1 > 255) {
    solenoid_command1 = 255;
  }

  /* Write our new commands to the solenoids! */
  analogWrite(solenoidPin1, solenoid_command0);
  analogWrite(solenoidPin2, solenoid_command0);
  analogWrite(solenoidPin3, solenoid_command1);
  analogWrite(solenoidPin4, solenoid_command1);
}

