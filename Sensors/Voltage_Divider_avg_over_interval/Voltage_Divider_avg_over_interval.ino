

/*===========================================================     Header     ==============================================================*/

//  Katelyn Rosethorn M.
//  Tuesday, September 19th

//  Reading from a voltage divider, this takes the average of the last n (interval) voltage measurements, 
//  calculates the unknown resistance from said measurements, and prints the average voltage and calculated
//  resistance each n measurements.

  
/*=========================================================   Define Constants   ==========================================================*/

//  Adjustable Constants:
//    - interval: The number of voltage measurements to average before calculating resistance
//    - Vout_pin: The analog port Vout is being measured from (plugged into)
//    - resistor_known: A voltage divider used to calculate an unknown resistance depends on a second known resistance. This is that resistance.
//              - (wow this is a really awkward phrasing)

const int interval = 2000;
const int Vout_pin = A0;
const int resistor_known = 1000;

//  Static Constants:
//      - voltage_in: 
//      - sensor_to_5V: scalar to shift analogRead(pin)'s integer between 0 and 1024 to the 0V to 5V ranges
    
const int voltage_in = 5; 
const float sensor_to_5V = 5.0 / 1023;

/*=========================================================   Initialization   ============================================================*/

//  Init variables:
//    - sensor_reading: Holds the reading from the sensor
//    - voltage_out: Calculated quantity representing the voltage loss over the unknown resistor
//              - (sensor_reading * sensor_to_5V)
//    - resistor_unknown: Calculated quantity representing the experimentally determined resistance of the unknown resistor
// 
//    - measurements: keeps track of measurements taken to calculate them every n measurements using modulo
//    - voltage sum: holds the voltage sum over n measurements to compute the average

int sensor_reading;
float voltage_out;
int resistor_unknown;

int measurements;
float voltage_sum;


// Setup function: 
//  - Initializes the Serial at 9600 bits/second

void setup() {
  Serial.begin(9600);

  measurements = 0;
  voltage_sum = 0.0;
}

/*=============================================================   Loop   ====================================================================*/


void loop() {

  // Read voltage and convert to 0 to 5V
  sensor_reading = analogRead(Vout_pin);
  voltage_out = sensor_reading*sensor_to_5V;
  
  // Add to the voltage sum for this interval
  voltage_sum = voltage_out + voltage_sum;
  measurements++;
  
  // When an interval is completed, the average is taken, resistance calculated, and both printed
  if (measurements % interval == 0){
    
    // Compute the average voltage over the last n trials
    voltage_out = voltage_sum/float(interval);
    
    // Calculate the unknown resistance
    resistor_unknown = (voltage_out * resistor_known) / (voltage_in-voltage_out);

    // Print Results
    // Serial.println("========================================================================");
    // Serial.println("Voltage out = " + String(voltage_out));
    // Serial.println("Unknown resistance = " + String(resistor_unknown));
    Serial.print("Voltage out: ");
    Serial.print(voltage_out);
    Serial.print("\tUnknown resistance: ");
    Serial.println(resistor_unknown);

    // Reset sum
    voltage_sum = 0;
  }  

}
