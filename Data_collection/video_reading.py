import cv2
import csv
import numpy as np
import pandas as pd
import os
file_path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\Data\sensor_data_6.csv"

data = pd.read_csv(file_path)

readings_dict = {row['Time(s)']: (row["R1(O)"], 
                                   row["R2(O)"], 
                                   row["R3(O)"], 
                                   row["R4(O)"]) for _, row in data.iterrows()}

print(readings_dict)

