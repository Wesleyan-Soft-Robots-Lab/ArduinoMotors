import os
import numpy as np
import pandas as pd

def combine_files():
    """
    Combines data of all files into one large csv file for training
    """

    data_path = r'C:\Users\softrobotslab\ArduinoMotors\Training_data'
    results = []
    files = os.listdir(data_path)
    for file in files:
        data = pd.read_csv(os.path.join(data_path, file))
        results.append(data)

    return results

if __name__ == '__main__':
    combine_files()

    
