import serial
import time
import os
import torch 
from Model.model import LSTMRegressor  # type: ignore
from Model.dataset import SerialRNNDataset  # type: ignore
from Model.train import prep_dataset
import numpy as np
import pandas as pd

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

batch_size = 1

lookback = 42

model = LSTMRegressor(input_size=4, batch_size=batch_size, num_layers=2,output_size=2)
model.load_state_dict(
    torch.load(
        f"Model/model/LSTMRegressor_strap_norm_{lookback}.pth", map_location=device, weights_only=True)
)    


dataset = SerialRNNDataset(lookback=lookback)
_, test_loader = prep_dataset(dataset, batch_size, test_size=0.99, shuffle=False)
test_array, target_array = dataset_to_numpy(test_loader)
# print(test_array[100], target_array[100])
# test_array = np.expand_dims(test_array, axis=2)

model.to(device)
model.eval()

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

# # Configure the serial connection
arduino_port = "COM3"  # Replace with your Arduino's COM port
baud_rate = 9600
# first = True
# Continuously send data
try:

    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    time.sleep(2)

    print('Connection to Arduino established. Waiting for data...')
    lookback_copy = lookback
    serialinput = []
    while True:
            try:
                if ser.in_waiting > 0:
                    while lookback_copy != 0:
                        parts = line.split()
                        r1, r2, r3 ,r4 = parts[1], parts[2], parts[3], parts[4] 
                        reading = np.array([r1, r2, r3, r4])
                        serialinput = np.concatenate(serialinput, reading, axis=0)
                        lookback_copy -= 1
                        continue
                    print(serialinput)
                    serialinput = torch.tensor(serialinput, dtype=torch.float32).unsqueeze(0).to(device)
                    with torch.no_grad():
                        pred = model(serialinput)

                    ser.write(pred.encode())  # Send data as bytes
                    print(f"Sent: {pred.strip()}")
                    time.sleep(1)  # Adjust rate of communication
                    line = ser.readline().decode('utf-8').strip()
                    print(f"Data from Arduino: {line}")
                    send_out = int(line.split()[-1])
                    processed_val = send_out*2 + 10
                    ser.write(f'{processed_val}\n'.encode())
                    print(f'Sent to Arduino: {processed_val}')
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
    # time_elapsed = stop - start
    # print(f"Time elapsed is {time_elapsed}")
    print("Serial connection closed.")