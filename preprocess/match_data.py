import os
import numpy as np
import pandas as pd

VIDEO_FPS = 60
SENSOR_SAMPLING_RATE = 42

def match_length(sensor_data: np.ndarray, video_data: np.ndarray) -> np.ndarray:
    """
    Matches the length of the sensor data to the length of the video data.

    Args:
        sensor_data (np.ndarray): The sensor data.
        video_data (np.ndarray): The video data.

    Returns:
        np.ndarray: The sensor data with matched length.
    """
    sensor_data = sensor_data[:video_data.shape[0] * SENSOR_SAMPLING_RATE // VIDEO_FPS]
    return sensor_data

def downsample_data(reference_data: np.ndarray, downsample_data: np.ndarray) -> np.ndarray:
    """
    Downsamples the given `downsample_data` array to match the length of the `reference_data` array.

    Parameters:
        reference_data (np.ndarray): The reference data array.
        downsample_data (np.ndarray): The data array to be downsampled.

    Returns:
        np.ndarray: The downsampled data array.

    """
    new_indices = np.linspace(0, len(downsample_data) - 1, reference_data.shape[0]).astype(int)
    downsampled_arr = np.interp(new_indices, np.arange(len(downsample_data)), downsample_data)
    return downsampled_arr

def remove_error_data(zipped_df: pd.DataFrame, resistence_threshold=10, angle_threshold=5) -> pd.DataFrame:
    """
    Removes error data from the given DataFrame based on a threshold difference.

    Args:
        zipped_df (pd.DataFrame): The DataFrame containing the data to be processed.
        threshold_difference (int, optional): The maximum allowed difference between the data and the average values. Defaults to 20.

    Returns:
        pd.DataFrame: The DataFrame with error data removed.
    """
    avg_values = np.mean(zipped_df[0])
    dropped_indices = []
    for index, row in zipped_df.iterrows():
        if abs(row[0][0] - avg_values[0]) > resistence_threshold or abs(row[0][1] - avg_values[1]) > resistence_threshold:
            # print(row[0][0], row[0][1])
            # print(index)
            zipped_df.at[index, 'E'] = 0
            dropped_indices.append(index)
        elif (index > 0) and (index-1 not in dropped_indices) and abs(row[1] - zipped_df.at[index-1, 1]) > angle_threshold: # type: ignore
            zipped_df.drop(index, inplace=True)
            dropped_indices.append(index)
            zipped_df.at[index, 'E'] = 0
        else:
            zipped_df.at[index, 'E'] = 1
    # print(zipped_df.index)
    return zipped_df

def match_serial_video_main():
    """
    Matches the serial data from strain sensors with video data.

    Returns:
        results (list): A list of pandas DataFrames containing the matched sensor data and video data.
    """
    sensor_data_path = 'Reader/balloon_data/Preprocessed'
    sensor_data = []
    for trial_num in range(1, 5):
        file = f'Trial_{trial_num}_serial.csv'
        trial_data = []
        df = pd.read_csv(os.path.join(sensor_data_path, file))
        for row in df['Data'].values:
            tmp = row.split(' ')
            time, r1, r2 = int(tmp[0]), float(tmp[1]), float(tmp[2])
            trial_data.append([r1, r2])
        sensor_data.append(np.array(trial_data))
    
    video_data_path = 'Data/balloon_data'
    results = []
    for trial_num in range(1,5):
        file = f'trial_{trial_num}.txt'
        video_data = np.loadtxt(os.path.join(video_data_path, file))
        sensor_data[trial_num-1] = match_length(sensor_data[trial_num-1], video_data)
        print(sensor_data[trial_num-1].shape, video_data.shape)
        if VIDEO_FPS < SENSOR_SAMPLING_RATE:
            sensor_data[trial_num-1] = downsample_data(video_data, sensor_data[trial_num-1])
        else:
            video_data = downsample_data(sensor_data[trial_num-1], video_data)
        
        zipped_df = pd.DataFrame(list(zip(sensor_data[trial_num-1], video_data)))
        zipped_df = remove_error_data(zipped_df)
        zipped_df.to_csv(f'Data/balloon_data/matched_data_trial_{trial_num}.csv')

        results.append(zipped_df)
    
    return results

if __name__ == '__main__':
    match_serial_video_main()
    
    

    