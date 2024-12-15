import pandas as pd
import os

sensor_file = r"C:\Users\softrobotslab\ArduinoMotors\sensor_data.csv"
angle_file = r"C:\Users\softrobotslab\ArduinoMotors\angles_output.csv"


def combine_files(sensors, angles):
    data = pd.DataFrame(columns = ['Time(s)',
                                   'R1(O)','R2(O)', 'R3(O)', 'R4(O)',
                                   'Angle1(deg)', 'Angle2(deg)'])
    
    sensor_dat = pd.read_csv(sensors)
    angle_dat = pd.read_csv(angles)
    sensor_dat = sensor_dat.values.tolist()
    angle_dat = angle_dat.values.tolist()
    for (r, a) in zip(sensor_dat, angle_dat):
        print(r, a)
        new_row = pd.DataFrame({'Time(s)': [r[0]],
                                        'R1(O)': [r[1]], 'R2(O)': [r[2]], 'R3(O)': [r[3]], 'R4(O)': [r[4]],
                                        'Angle1(deg)': [a[1]], 'Angle2(deg)':[a[2]]})
        data = pd.concat([data,new_row], ignore_index=True)
if __name__ == '__main__':
    combine_files(sensor_file, angle_file)
    