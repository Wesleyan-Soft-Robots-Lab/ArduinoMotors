import serial
import pandas as pd
import time
'''
Daniel Bench
Friday 11/1

Reading from voltage and resistance script and using pandas to create a csv file with the organized data
'''

# Configure serial port (adjust 'COM3' to Arduino port)
ser = serial.Serial('COM5', 9600)
time.sleep(2)  

# Creating empty .csv file
data = pd.DataFrame(columns=['Time(s)',
                             'R1 (O)',
                              'R2(O)', 
                              'R3(O)', 
                              'R4(O)'])

start_time = time.time()
# Throw exception in event data collecting stops
try:
    while True:
        # Read data from arduino script
        line = ser.readline().decode('utf-8').strip()
        # print(line)
        # if "Voltage out:" in line:
        # Extract values from the line
        parts = line.split()
        # print(parts)
        timed = time.time()-start_time
        timed = round(timed, 2)
        resistance1 = parts[1]
        resistance2 = parts[2]
        resistance3 = parts[3]
        resistance4 = parts[4]
        print(timed,resistance1, resistance2, resistance3, resistance4)

        # Append to DataFrame
        new_row = pd.DataFrame({'Time(s)': [timed],
                                'R1(O)': [resistance1], 
                                'R2(O)': [resistance2], 
                                'R3(O)': [resistance3], 
                                'R4(O)': [resistance4]})
        data = pd.concat([data,new_row], ignore_index=True)
        # print(f"Voltage Out: {voltage} V, Time: {timed} Ohms")

except KeyboardInterrupt:
    print("Data collection stopped.")

finally:
    # Save to CSV when the script ends
    data.to_csv('sensor_data.csv', index=False)
    print("Data saved to 'sensor_data.csv'.")
    ser.close()
