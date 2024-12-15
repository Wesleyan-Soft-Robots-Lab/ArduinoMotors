import numpy as np

path = "Reader/balloon_data/serial_data_17.23.51.csv"
threshold_time = 410803


def read_data(path, threshold_time):
    """
    Read sensor data from the serial file and preprocess it.

    Args:
        path (str): The path to the file containing the sensor data.
        threshold_time (int): The threshold time for filtering the data.

    Returns:
        numpy.ndarray: A numpy array containing the preprocessed sensor data.
    """
    sensor_data = []
    with open(path, "r") as file:
        data = file.read().split("\n")
        for line in data[1:]:
            try:
                reading = line.split(",")[1].split(" ")
                if int(reading[0]) < threshold_time:
                    continue
                else:
                    sensor_data.append([reading[1], reading[2]])
            except:
                pass
    return np.array(sensor_data).astype(float)


def flag_data(sensor_data, threshold_resistance=10):
    """
    Flags the sensor data based on a threshold resistance value. If the resistance value is above the threshold, the 
    data point is flagged as 0, otherwise it is flagged as 1.

    Args:
        sensor_data (numpy.ndarray): Array of sensor data.
        threshold_resistance (float, optional): Threshold resistance value. Defaults to 10.

    Returns:
        numpy.ndarray: Array of flags indicating whether each data point is above or below the threshold resistance.
    """
    data_flag = np.ones(sensor_data.shape[0])
    for x in range(len(sensor_data)):
        if (
            abs(sensor_data[x][0]) > threshold_resistance
            or abs(sensor_data[x][1]) > threshold_resistance
        ):
            data_flag[x] = 0
        else:
            data_flag[x] = 1
    return data_flag


sensor_data = read_data(path, threshold_time)
sensor_data -= sensor_data[0]
data_flag = flag_data(sensor_data)
print(sensor_data)
# with the data_flag as mask, find the max and min value of the data
print(sensor_data[data_flag == 1].max())
print(sensor_data[data_flag == 1].min())
