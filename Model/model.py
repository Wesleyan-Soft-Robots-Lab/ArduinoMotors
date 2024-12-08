import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

if torch.cuda.is_available():
    device = torch.device('cuda')
elif torch.backends.mps.is_available():
    device = torch.device('mps')
else:
    device = torch.device('cpu')
class LinearClassifier(nn.Module):
    def __init__(self, batch_size: int):
        super().__init__()
        self.linear1 = nn.Linear(16, 8)
        self.linear2 = nn.Linear(8, 5)
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)
        self.linear3 = nn.Linear(16,5)
    
    def forward(self, x):
        # x = self.relu(self.linear1(x))
        # x = self.linear2(x)
        x = self.linear3(x)
        return x
    
class ConvClassifier(nn.Module):
    def __init__(self, batch_size: int):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool1d(2)
        self.relu = nn.ReLU()
        self.flatten = nn.Flatten()
        self.linear1 = nn.Linear(128, 5)
    
    def forward(self, x):
        batch_size = x.size(0)
        x = self.relu(self.pool(self.conv1(x)))
        x = self.flatten(x)
        x = self.linear1(x)
        return x
    
    
class LSTMRegressor(nn.Module):
    def __init__(self, input_size, batch_size, hidden_size=16, num_layers=1, output_size=2):
        super(LSTMRegressor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_size = batch_size
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size, dtype=torch.float32).to(device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size, dtype=torch.float32).to(device)
        for pos in range(x.size(1)):
            out, (h0, c0) = self.lstm(x[:,pos,:].unsqueeze(1), (h0, c0))
        out = self.fc(out[:, -1, :])
        return out[:, 0]

class FCRegressor(nn.Module):
    def __init__(self, input_size, batch_size):
        super(FCRegressor, self).__init__()
        self.fc1 = nn.Linear(input_size, 16)
        self.fc2 = nn.Linear(16, 8)
        self.fc3 = nn.Linear(8, 1)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x[:, 0, 0]