import serial
import time
import torch 
from Model.model import LSTMRegressor  # type: ignore
from Model.dataset import SerialRNNDataset  # type: ignore
from Model.train import prep_dataset
import numpy as np

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
        f"Model/model/LSTMRegressor_strap_norm_{lookback}.pth", map_location=device)
)    


dataset = SerialRNNDataset(lookback=lookback)
_, test_loader = prep_dataset(dataset, batch_size, test_size=0.99, shuffle=False)
test_array, target_array = dataset_to_numpy(test_loader)
# print(test_array[100], target_array[100])
# test_array = np.expand_dims(test_array, axis=2)

model.to(device)
model.eval()

for i in range(len(test_array)-100, len(test_array)):
    # print(f"Test Sample: {test_array[i]}, Target: {target_array[i]}")
    # print(test_array[i].shape)
    input = torch.tensor(test_array[i], dtype=torch.float32).unsqueeze(1).to(device) 

    with torch.no_grad():
        prediction = model(input)

    print(f'{test_array[i]}\t{90*prediction[-1]}\t{90*target_array[i]}')
    
# print('for fun')


# # Configure the serial connection
# arduino_port = "COM5"  # Replace with your Arduino's COM port
# baud_rate = 9600
# ser = serial.Serial(arduino_port, baud_rate, timeout=1)





# # Continuously send data
# try:
#     while True:
#         line = ser.readline().decode('utf-8').strip()

#         parts = line.split()
#         r1, r2, r3 ,r4, a1, a2 = parts[1], parts[2], parts[3], parts[4], \
#         parts[5], parts[6] 
#         serialinput = np.array([r1, r2, r3, r4])
#         serialinput = np.expand_dims(serialinput, axis=2)
#         with torch.no_grad():
#             pred = model(serialinput)

#         ser.write(pred.encode())  # Send data as bytes
#         print(f"Sent: {pred.strip()}")
#         # time.sleep(1)  # Adjust rate of communication
# except KeyboardInterrupt:
#     print("Communication stopped.")
# finally:
#     ser.close()