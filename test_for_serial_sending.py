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
input_init = np.array([[ 95.25, 89.45, 102.54, 98.7 ],
 [ 95.21, 89.34, 102.48, 98.68],
 [ 95.18, 89.22, 102.46, 98.65],
 [ 95.13, 89.13, 102.46, 98.63],
 [ 95.08, 88.99, 102.46, 98.6 ],
 [ 95.03, 88.9, 102.43, 98.55],
 [ 95.01, 88.8, 102.48, 98.5 ],
 [ 94.96, 88.71, 102.46, 98.47],
 [ 94.91, 88.59, 102.48, 98.45],
 [ 94.88, 88.53, 102.43, 98.4 ],
 [ 94.83, 88.43, 102.38, 98.34],
 [ 94.78, 88.3, 102.35, 98.32],
 [ 94.76, 88.18, 102.32, 98.27],
 [ 94.71, 88.09, 102.24, 98.19],
 [ 94.64, 88.,  102.19, 98.16],
 [ 94.66, 87.95, 102.24, 98.19],
 [ 94.69, 88.02, 102.27, 98.16],
 [ 94.66, 88.04, 102.24, 98.14],
 [ 94.66, 88.02, 102.19, 98.14],
 [ 94.69, 88.07, 102.11, 98.11],
 [ 94.66, 88.07, 102.08, 98.11],
 [ 94.64, 88.04, 102.08, 98.14],
 [ 94.66, 88.04, 102.14, 98.11],
 [ 94.68, 88.07, 102.08, 98.09],
 [ 94.66, 88.04, 102.08, 98.11],
 [ 94.66, 88.02, 102.14, 98.14],
 [ 94.68, 88.09, 102.16, 98.11],
 [ 94.64, 88.09, 102.19, 98.11],
 [ 94.64, 88.04, 102.35, 98.16],
 [ 94.68, 88.04, 102.38, 98.14],
 [ 94.66, 88.04, 102.46, 98.09],
 [ 94.64, 88.02, 102.59, 98.11],
 [ 94.66, 88.02, 102.62, 98.14],
 [ 94.68, 88.07, 102.7,  98.11],
 [ 94.66, 88.07, 102.59, 98.11],
 [ 94.66, 88.04, 102.67, 98.14],
 [ 94.66, 88.04, 102.59, 98.14],
 [ 94.61, 88.04, 102.51, 98.14],
 [ 94.61, 88.04, 102.48, 98.14],
 [ 94.64, 88.04, 102.56, 98.11],
 [ 94.64, 88.04, 102.59, 98.11],
 [ 94.61, 88.02, 102.59, 98.11]])

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
    arduino_port = "COM7"  # Replace with your Arduino's COM port
    baud_rate = 9600
    lstm_model = prepare_model()
    # Continuously send data
    try:

        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)

        print('Connection to Arduino established. Waiting for data...')
        lookback_copy = LOOKBACK
        serialinput = np.empty((0,4)) #input filled with values that match our lookback value
        first = True
        init_first = True
        while True:
                try:
                    if isinstance(serialinput, torch.Tensor):
                        serialinput = serialinput.cpu().numpy()
                    if ser.in_waiting > 0:
                        if first:
                            first = False
                            continue
                        elif lookback_copy > 1: #we fill input until we have enough values for the model
                            line = ser.readline().decode('utf-8').strip()
                            # print(line)
                            parts = line.split()
                            r1, r2, r3 ,r4 = parts[1], parts[2], parts[3], parts[4]
                            r1, r2, r3, r4 = float(r1), float(r2), float(r3), float(r4)
                            reading = np.array([r1, r2, r3, r4])
                            serialinput = np.append(serialinput, [np.array(reading)], axis=0)
                            lookback_copy -= 1
                            continue
                        elif serialinput.shape[0] != LOOKBACK:
                            # print(serialinput)
                            line = ser.readline().decode('utf-8').strip()
                            # print(line)
                            parts = line.split()
                            r1, r2, r3 ,r4 = parts[1], parts[2], parts[3], parts[4]
                            r1, r2, r3, r4 = float(r1), float(r2), float(r3), float(r4)
                            reading = np.array([r1, r2, r3, r4])
                            serialinput = np.append(serialinput, [np.array(reading)], axis=0)
                            # if init_first:
                            #     input_init = serialinput
                            #     init_first = False
                        # print(serialinput)
                        input = (serialinput - input_init)/input_init
                        input = torch.tensor(input, dtype=torch.float32).unsqueeze(0).to(device)
                        with torch.no_grad():
                            pred = lstm_model(input)
                        pred = pred.cpu().numpy()
                        # pred = f"{pred[0]*90}".encode()
                        ser.write(f"{pred[0]*90}".encode())  # Send data as bytes
                        # print(f"Sent: {pred[0]*90}")
                        response = ser.readline().decode('utf-8').strip()
                        # if response:
                        #     print("Received: ", response)
                        # serialinput = serialinput.squeeze(0)
                        serialinput = serialinput[1:]
                        # print(serialinput.shape)
                    time.sleep(0.1) #for minimal data congestion

                except ValueError:
                    print("Value error: invalid data received.")
                    line = ser.readline().decode('utf-8').strip()
                    print(line)
                    # parts = line.split()
                    # r1, r2, r3 ,r4 = parts[1], parts[2], parts[3], parts[4]
                    # r1, r2, r3, r4 = float(r1), float(r2), float(r3), float(r4)
                    # reading = np.array([r1, r2, r3, r4])
                    # print(reading.shape)
                    # print(serialinput.shape)
                    # serialinput = np.append(serialinput, reading, axis=0)
                    # print(serialinput)
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