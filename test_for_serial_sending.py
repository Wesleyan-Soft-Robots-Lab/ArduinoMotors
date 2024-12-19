import serial
import time
import os
import torch 
from Model.model import LSTMRegressor  # type: ignore
from Model.dataset import SerialRNNDataset  # type: ignore
from Model.train import prep_dataset
import numpy as np
import pandas as pd

LOOKBACK = 42
batch_size = 1

if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"Using device: {device}")

def dataset_to_numpy(dataloader) -> tuple[np.ndarray, np.ndarray]:
    batches = []
    targets = []
    for data, target in dataloader:
        batches.append(data.numpy())
        targets.append(target.numpy())
    return np.concatenate(batches), np.concatenate(targets)



def prepare_model():
    model = LSTMRegressor(input_size=4, batch_size=batch_size, num_layers=2,output_size=2)
    model.load_state_dict(
        torch.load(
            f"Model/model/LSTMRegressor_strap_norm_{LOOKBACK}.pth", map_location=device, weights_only=True)
    ) 
    return model


# # Configure the serial connection
arduino_port = "COM3"  # Replace with your Arduino's COM port
baud_rate = 9600




def arduino_predictions():

    lstm_model = prepare_model()
    lstm_model.to(device)
    lstm_model.eval()
    # Continuously send data
    try:

        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)

        print('Connection to Arduino established. Waiting for data...')
        lookback_copy = LOOKBACK
        serialinput = []
        while True:
                try:
                    if ser.in_waiting > 0:
                        while lookback_copy != 0:
                            line = ser.readline().decode('utf-8').strip()
                            parts = line.split()
                            r1, r2, r3 ,r4 = parts[1], parts[2], parts[3], parts[4] 
                            reading = np.array([r1, r2, r3, r4])
                            # print(reading)
                            serialinput = np.append(serialinput, reading, axis=0)
                            lookback_copy -= 1
                            continue
                        print(serialinput)
                        lookback_copy = LOOKBACK
                        serialinput = []
                        serialinput = torch.tensor(serialinput, dtype=torch.float32).unsqueeze(0).to(device)
                        with torch.no_grad():
                            pred = lstm_model(serialinput)

                        ser.write(pred.encode())  # Send data as bytes
                        print(f"Sent: {pred.strip()}")
                    time.sleep(0.1)
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

    # dataset = SerialRNNDataset(lookback=LOOKBACK)
# _, test_loader = prep_dataset(dataset, batch_size, test_size=0.99, shuffle=False)
# test_array, target_array = dataset_to_numpy(test_loader)
# print(test_array[100], target_array[100])
# test_array = np.expand_dims(test_array, axis=2)


# data = pd.DataFrame(columns = ['Angle Prediction1', 'Angle prediction2', 'Angle Real1', 'Angle Real2'])

# for i in range(len(test_array)-100, len(test_array)):
#     # print(f"Test Sample: {test_array[i]}, Target: {target_array[i]}")
#     # print(test_array[i].shape)
#     input = torch.tensor(test_array[i], dtype=torch.float32).unsqueeze(0).to(device) 

#     with torch.no_grad():
#         prediction = model(input)
#         output = prediction.cpu().numpy()
#     new_row = pd.DataFrame({'Angle Prediction1': [90*prediction[-1].cpu().numpy()[0]], 'Angle prediction2': [90*prediction[-1].cpu().numpy()[1]], 
#                             'Angle Real1': [90*target_array[i][0]], 'Angle Real2': [90*target_array[i][1]]})
#     data = pd.concat([data, new_row], ignore_index=True)
#     # print(f'{90*prediction[-1]}\t{90*target_array[i]}')

# dir_path = r'C:\Users\Chrispc2002\OneDrive\Documents\Research\ArduinoMotors\predictions'
# data_name = 'predictions1.csv'

# data.to_csv(os.path.join(dir_path, data_name), index=False)
# # print('for fun')