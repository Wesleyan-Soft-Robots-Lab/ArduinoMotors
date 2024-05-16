<h1>**Connecting and Controlling Air Valves with Arduino: A Step-by-Step Guide**.</h1>

<h2> Components: </h2> 
<br/>

<img width=50% alt="Screenshot 2024-05-16 at 12 03 09 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/80cd22cb-9920-454d-a2fb-8864d9162217">

MOSFET Transistor

<br/>
<img width=50% alt="Screenshot 2024-05-16 at 12 10 07 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/6e36a5b2-7278-477a-ba43-9ad5bfc8f4bb">

Breadboard

<br/>
<img width=50% alt="Screenshot 2024-05-16 at 12 22 10 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/d84adf26-b431-4be2-bfc4-ff59789dcc5a">

Diode

<br/>
<img width=50% alt="Screenshot 2024-05-16 at 12 22 42 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/61be64dd-db8d-4bb7-ba41-0eb63814defd">

(Insert Ohms) Resistor

<br/>
<img width=50% alt="Screenshot 2024-05-16 at 12 26 24 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/171faa60-e1bf-4520-acf5-c826fc3e3036">

6V Air valve 

<br/>
<img width=50% alt="Screenshot 2024-05-16 at 12 26 54 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/35518746-c7bf-476c-8467-23bf62103a79">

Jumper wires
<br/>
<img width=50% alt="Screenshot 2024-05-16 at 12 29 15 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/401a9782-79e4-4735-ac03-504b59e04322">

Balloons

<br/>
<img width=50% alt="Screenshot 2024-05-16 at 12 29 45 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/610c7067-3998-41e3-8d90-e5bdd6159039">

Plastic cap (for ballons)

<br/>
<img width=50% alt="Screenshot 2024-05-16 at 12 30 14 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/a9c63cc8-47cb-4c76-aa91-367d94c67fb1">

Expandable sleeving

<br/>
<img width=50% alt="Screenshot 2024-05-16 at 12 30 38 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/02c3c481-b3f7-4156-a6b4-75d7e91623c7">

Potentiometer

<br/>
<img width=50% alt="Screenshot 2024-05-16 at 12 31 13 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/3e81f375-d412-4c7c-9c18-d13b6c1b42bf">

Everything!

<h2> How to put together: </h2>


<img width="1271" alt="Screenshot 2024-05-16 at 1 38 58 PM" src="https://github.com/Wesleyan-Soft-Robots-Lab/ArduinoMotors/assets/26982745/0a8036aa-f129-4655-9201-5b5f901baa98">

In the image, a DC motor is displayed, but substituting it with an air valve will work seamlessly with the demonstrated connections. (Note: This setup shows the connection for a single air valve. If additional valves are needed, connect them similarly to different Analog and Digital pins, and update the code accordingly to account for these changes.)


1. **Arduino Power Supply**:
  - The Arduino receives power through the USB port, providing 5V and ground (GND) to the board. However, since we will be using 6.5V air valves, an external power supply is necessary. This can be connected either through the Arduino's port or directly to the breadboard.

2. **Potentiometer Connections**:
   - **Left Pin (VCC)**: The left pin of the potentiometer is connected to the 5V/Vin power rail on the breadboard. This supplies the potentiometer with a constant 5V.
   - **Middle Pin (Output)**: The middle pin of the potentiometer (the wiper) is connected to the analog pin A0 on the Arduino via a purple wire. This pin outputs a variable voltage (depending on the position of the potentiometer knob) between 0V and 5V.
   - **Right Pin (GND)**: The right pin of the potentiometer is connected to the ground (GND) rail on the breadboard. This completes the circuit for the potentiometer, allowing it to divide the 5V across its range.

3. **Breadboard Power Rails**:
   - **Red Rail**: The red power rail on the breadboard is connected to the 5V/Vin pin on the Arduino via a red wire. This rail provides 5V to components on the breadboard.
   - **Blue Rail**: The blue ground rail on the breadboard is connected to a GND pin on the Arduino via a blue wire. This rail provides a common ground to the components on the breadboard.

4. **NMOS Transistor Connections**:
   - **Gate (G)**: The gate pin of the NMOS transistor is connected to digital pin 13 on the Arduino via an orange wire. This pin controls the transistor's switching, turning it on and off.
   - **Drain (D)**: The drain pin of the NMOS transistor is connected to one terminal of the motor (Air Valve). When the transistor is turned on, current flows from the drain to the source, allowing the motor (Air Valve) to operate.
   - **Source (S)**: The source pin of the NMOS transistor is connected to the ground rail on the breadboard. This provides a path for current to flow through the transistor when it is turned on.

5. **Motor Connections**:
   - **Negative Terminal**: The negative terminal of the motor is connected to the drain (D) of the NMOS transistor. This allows the motor to be controlled by the transistor.
   - **Positive Terminal**: The positive terminal of the motor is connected to the 5V power rail on the breadboard. This supplies the motor with power.

6. **Diode**:
   - The diode is connected across the motor terminals. The cathode (marked end) is connected to the positive terminal of the motor, and the anode is connected to the drain (D) of the NMOS transistor. This diode protects the circuit from voltage spikes caused by the inductive load of the motor.

7. **Current-Limiting Resistor**:
   - A resistor is connected between the gate (G) of the NMOS transistor and digital pin 13 on the Arduino. This resistor limits the current flowing into the gate of the transistor, protecting the Arduino pin.

### How It Works
- When you rotate the potentiometer, it changes the voltage at its middle pin, which is read by the Arduino on analog pin A0.
- The Arduino processes this analog reading to set the output signal on digital pin 13. If the signal is high, the air valve opens and closes rapidly; if the signal is low, the opposite happens (refer to the code to understand the detailed logic).



































