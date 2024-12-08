import os
import numpy as np
import pandas as pd
import csv

def combine_files():
    """
    Combines data of all files into one large csv file for training
    """

    data_path = r'C:\Users\softrobotslab\ArduinoMotors\Training_data_angle'
    # print('hello')
    results = []
    sensor_data = []
    files = os.listdir(data_path)
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(data_path, file)
            data = pd.read_csv(file_path)
            trial_data = []
            for _, row in data.iterrows():
                r1,r2,r3,r4 = float(row.iloc[1]), float(row.iloc[2]), float(row.iloc[3]), float(row.iloc[4])
                a1, a2 = float(row.iloc[5]), float(row.iloc[6])
                trial_data.append(([r1,r2,r3,r4], [a1,a2]))
            # print(len(trial_data))
            df = pd.DataFrame(list(trial_data))
            results.append(df)
        # print(results)
    return results

if __name__ == '__main__':
    combine_files()

    
