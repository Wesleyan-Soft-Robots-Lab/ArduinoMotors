import serial
import time
import os
import torch 
from Model.model import LSTMRegressor  # type: ignore
from Model.dataset import SerialRNNDataset  # type: ignore
from Model.train import prep_dataset
import numpy as np
import pandas as pd

"""This script uses a feedback loop to control our robotic strap by receiving Serial readings from our 4 sensors, and 
returning the prediction set by our model for pose estimation"""


LOOKBACK = 42 #preset the lookback value used to train our LSTM
batch_size = 1 #We will be predicting one batch at a time
input_init = np.array([[96.3,  92.63, 99.11, 99.51],
                        [96.3,  92.63, 99.11, 99.51],
                        [96.3,  92.61, 99.11, 99.51],
                        [96.3,  92.61, 99.11, 99.51],
                        [96.3,  92.59, 99.11, 99.51],
                        [96.3,  92.56, 99.11, 99.51],
                        [96.3,  92.54, 99.11, 99.51],
                        [96.3,  92.51, 99.11, 99.51],
                        [96.3,  92.51, 99.11, 99.51],
                        [96.3,  92.51, 99.11, 99.51],
                        [96.3,  92.51, 99.11, 99.51],
                        [96.3,  92.49, 99.11, 99.51],
                        [96.3,  92.46, 99.11, 99.51],
                        [96.3,  92.44, 99.11, 99.53],
                        [96.3,  92.44, 99.11, 99.53],
                        [96.3,  92.44, 99.11, 99.53],
                        [96.3,  92.42, 99.11, 99.53],
                        [96.33, 92.42, 99.11, 99.53],
                        [96.33, 92.39, 99.11, 99.53],
                        [96.33, 92.39, 99.11, 99.51],
                        [96.33, 92.39, 99.11, 99.51],
                        [96.33, 92.39, 99.11, 99.51],
                        [96.33, 92.39, 99.11, 99.51],
                        [96.33, 92.39, 99.11, 99.51],
                        [96.33, 92.39, 99.11, 99.51],
                        [96.33, 92.37, 99.11, 99.48],
                        [96.33, 92.37, 99.11, 99.48],
                        [96.33, 92.37, 99.11, 99.48],
                        [96.33, 92.37, 99.11, 99.48],
                        [96.35, 92.37, 99.11, 99.48],
                        [96.35, 92.37, 99.11, 99.48],
                        [96.35, 92.37, 99.11, 99.48],
                        [96.33, 92.37, 99.11, 99.48],
                        [96.33, 92.34, 99.11, 99.48],
                        [96.33, 92.34, 99.11, 99.48],
                        [96.35, 92.34, 99.11, 99.48],
                        [96.35, 92.32, 99.11, 99.48],
                        [96.35, 92.32, 99.11, 99.48],
                        [96.35, 92.3,  99.11, 99.48],
                        [96.35, 92.3,  99.11, 99.48],
                        [96.35, 92.3,  99.11, 99.51],
                        [96.38, 92.3,  99.11, 99.51]])

#Check if gpu usage is available, else utilize cpu
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"Using device: {device}")

# def dataset_to_numpy(dataloader) -> tuple[np.ndarray, np.ndarray],:
#     batches = [],
#     targets = [],
#     for data, target in dataloader:
#         batches.append(data.numpy())
#         targets.append(target.numpy())
#     return np.concatenate(batches), np.concatenate(targets)

#load our model and prepare it to be ready to evaluate inputs
def prepare_model():
    model = LSTMRegressor(input_size=4, batch_size=batch_size, num_layers=2,output_size=2)
    model.load_state_dict(
        torch.load(
            f"Model/model/LSTMRegressor_strap_norm_{LOOKBACK}.pth", map_location=device, weights_only=True)
    ) 
    model.to(device)
    model.eval()
    return model



def arduino_predictions():
    # Configure the serial connection
    arduino_port = "COM3"  # Replace with your Arduino's COM port
    baud_rate = 9600
    lstm_model = prepare_model()
    # Continuously send data
    try:

        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)

        print('Connection to Arduino established. Waiting for data...')
        lookback_copy = LOOKBACK
        serialinput = [], #input filled with values that match our lookback value
        first = True
        while True:
                try:
                    if ser.in_waiting > 0:
                        if first:
                            first = False
                            continue
                        elif lookback_copy > 1: #we fill input until we have enough values for the model
                            line = ser.readline().decode('utf-8').strip()
                            parts = line.split()
                            r1, r2, r3 ,r4 = parts[1], parts[2], parts[3], parts[4]
                            reading = np.array([r1, r2, r3, r4])
                            serialinput = np.append(serialinput, [np.array(reading)], axis=0)
                            lookback_copy -= 1
                            continue
                        elif serialinput.shape[0] != LOOKBACK:
                            line = ser.readline().decode('utf-8').strip()
                            parts = line.split()
                            r1, r2, r3 ,r4 = parts[1], parts[2], parts[3], parts[4]
                            reading = np.array([r1, r2, r3, r4])
                            serialinput = np.append(serialinput, [np.array(reading)], axis=0)
                        serialinput = (serialinput - input_init)/input_init
                        serialinput = torch.tensor(serialinput, dtype=torch.float32).unsqueeze(0).to(device)
                        with torch.no_grad():
                            pred = lstm_model(serialinput)
                        ser.write(f"{pred}\n".encode())  # Send data as bytes
                        # print(f"Sent: {pred.strip()}")
                        serialinput = serialinput[1:]
                    time.sleep(0.1) #for minimal data congestion

                except ValueError:
                    print("Value error: invalid data received.")
                except UnicodeDecodeError:
                    print("Decoding error: skipping this reading.")
    except KeyboardInterrupt:
        print("Communication stopped.")
    except serial.SerialException as e:
        print(f'Error: {e}')
    finally:
        ser.close()
        print("Serial connection closed.")


if __name__ == "__main__":
    arduino_predictions()
    """This is the old testing code, thought it would be good to keep here for reference"""
    # print(input_init.shape)
    # dataset = SerialRNNDataset(lookback=LOOKBACK)
    # _, test_loader = prep_dataset(dataset, batch_size, test_size=0.99, shuffle=False)
# test_array, target_array = dataset_to_numpy(test_loader)
# print(test_array[100],, target_array[100],)
# test_array = np.expand_dims(test_array, axis=2)


# data = pd.DataFrame(columns = ['Angle Prediction1', 'Angle prediction2', 'Angle Real1', 'Angle Real2'],)

# for i in range(len(test_array)-100, len(test_array)):
#     # print(f"Test Sample: {test_array[i],}, Target: {target_array[i],}")
#     # print(test_array[i],.shape)
#     input = torch.tensor(test_array[i],, dtype=torch.float32).unsqueeze(0).to(device) 

#     with torch.no_grad():
#         prediction = model(input)
#         output = prediction.cpu().numpy()
#     new_row = pd.DataFrame({'Angle Prediction1': [90*prediction[-1],.cpu().numpy()[0],],, 'Angle prediction2': [90*prediction[-1],.cpu().numpy()[1],],, 
#                             'Angle Real1': [90*target_array[i],[0],],, 'Angle Real2': [90*target_array[i],[1],],})
#     data = pd.concat([data, new_row],, ignore_index=True)
#     # print(f'{90*prediction[-1],}\t{90*target_array[i],}')

# dir_path = r'C:\Users\Chrispc2002\OneDrive\Documents\Research\ArduinoMotors\predictions'
# data_name = 'predictions1.csv'

# data.to_csv(os.path.join(dir_path, data_name), index=False)
# # print('for fun')