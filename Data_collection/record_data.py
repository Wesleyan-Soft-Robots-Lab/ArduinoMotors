import cv2
import os
import shutil
import serial

import pandas as pd
import time
'''
Patton
Sunday 12/1

This script records data from a webcam and a sensor and saves it to a directory.
'''

###############################
### Initializations
###############################

DATA_DIRECTORY = r"TestData\take6"
FRAMES_PER_SECOND = 20 # adjust to the frame rate
DURATION = 45 # adjust to the duration
WEBCAM_INDEX = 1 # adjust to the webcam index
VERBOSE = False # adjust to True to print more information

ser = serial.Serial('COM7', 9600)
time.sleep(2)  

cap = cv2.VideoCapture(WEBCAM_INDEX) 
if not cap.isOpened():
    print("Error: Could not open webcam.")

sensor_data = pd.DataFrame(columns=['Time(s)', 'R1(O)', 'R2(O)', 'R3(O)', 'R4(O)'])

###############################
### Functions
###############################

def webcam_record(count):
    """ Record a frame from the webcam.
    """
    ret, frame = cap.read()
        
    if not ret:
        print("Error: Failed to capture frame.")

    filename = os.path.join(DATA_DIRECTORY, f"image_{count}_{time.time()}.jpg")
    cv2.imwrite(filename, frame)

    if VERBOSE: 
        cv2.imshow("Captured Frame", frame)
        print(f"Saved {filename}")

def sensor_record():
    """ Record a line of data from the sensor
    """
    global sensor_data
    line = ser.readline().decode('utf-8').strip()
    # Extract values from the line
    parts = line.split()
    timed = time.time()
    resistance1 = parts[2]
    resistance2 = parts[3]
    resistance3 = parts[4]
    resistance4 = parts[5]

    # Append to DataFrame
    new_row = pd.DataFrame({'Time(s)': [timed],
                            'R1(O)': [resistance1], 
                            'R2(O)': [resistance2], 
                            'R3(O)': [resistance3], 
                            'R4(O)': [resistance4]})
    sensor_data = pd.concat([sensor_data,new_row], ignore_index=True)
    
    if VERBOSE:
        print(timed,resistance1, resistance2, resistance3, resistance4)

def record():
    
    if os.path.exists(DATA_DIRECTORY):
        shutil.rmtree(DATA_DIRECTORY)
    os.makedirs(DATA_DIRECTORY)

    interval = 1/FRAMES_PER_SECOND
    start_time = time.time()
    last_time = start_time
    count = 0
    
    while time.time() - start_time < DURATION:
        curr_time = time.time()
        if curr_time - last_time < interval:
            continue
        
        webcam_record(count)
        sensor_record()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        count += 1
        last_time = curr_time
    
    sensor_data.to_csv(f'{DATA_DIRECTORY}\sensor_data.csv', index=False)
    cap.release()
    cv2.destroyAllWindows()
    ser.close()
    
    print(f"frames per second {count/DURATION}")
    
if __name__ == "__main__":
    record()