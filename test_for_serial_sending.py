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
model = LSTMRegressor(input_size=4, batch_size=batch_size, num_layers=2,output_size=2)
model.load_state_dict(
    torch.load(
        f"Model/model/LSTMRegressor_strap_42.pth", map_location=torch.device("cuda")
    )
)    

model.eval()



dataset = SerialRNNDataset(lookback=42)
_, test_loader = prep_dataset(dataset, batch_size, test_size=0.99)
test_array, target_array = dataset_to_numpy(test_loader)
test_array = np.expand_dims(test_array, axis=2)
input = torch.tensor(test_array[0])

model.to(device)
input = input.to(device)

with torch.no_grad():
    prediction = model(input)

print('prediction:', 90*prediction)
print('real: ', target_array[0])

print('for fun')


# # Configure the serial connection
# arduino_port = "COM5"  # Replace with your Arduino's COM port
# baud_rate = 9600
# ser = serial.Serial(arduino_port, baud_rate, timeout=1)





# # Continuously send data
# try:
#     while True:
#         data = "Hello Arduino\n"  # Add newline to match Arduino's readStringUntil
#         ser.write(data.encode())  # Send data as bytes
#         print(f"Sent: {data.strip()}")
#         time.sleep(1)  # Adjust rate of communication
# except KeyboardInterrupt:
#     print("Communication stopped.")
# finally:
#     ser.close()