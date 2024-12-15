import torch
from torch.quantization import quantize_dynamic


model = torch.load(r'C:\Users\softrobotslab\ArduinoMotors\Model\model\LSTMRegressor_strap_42.pth')

model.eval()

quantized_model = quantize_dynamic(model, {torch.nn.LSTM})