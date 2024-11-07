import serial
import pandas as pd
import time
'''
Daniel Bench
Friday 11/1

Reading from voltage and resistance script and using pandas to create a csv file with the organized data
'''

# Configure serial port (adjust 'COM3' to Arduino port)
ser = serial.Serial('COM3', 9600)
time.sleep(2)  

# Creating empty .csv file
data = pd.DataFrame(columns=['Voltage', 'Resistance'])


# Throw exception in event data collecting stops
try:
    while True:
        # Read data from arduino script
        line = ser.readline().decode('utf-8').strip()
        
        if "Voltage out:" in line:
            # Extract values from the line
            parts = line.split("\t")
            voltage = float(parts[0].split(":")[1].strip())
            resistance = int(parts[1].split(":")[1].strip())

            # Append to DataFrame
            data = data.append({'Voltage Out (V)': voltage, 'Resistance (Ohms)': resistance}, ignore_index=True)
            print(f"Voltage Out: {voltage} V, Resistance: {resistance} Ohms")

except KeyboardInterrupt:
    print("Data collection stopped.")

finally:
    # Save to CSV when the script ends
    data.to_csv('sensor_data.csv', index=False)
    print("Data saved to 'sensor_data.csv'.")
    ser.close()
