import os, sys
import numpy as np
import torch
import matplotlib.pyplot as plt # type: ignore
import time

sys.path.append(".")
from Model.model import LSTMRegressor # type: ignore
from Model.dataset import SerialRNNDataset # type: ignore
from Model.train import prep_dataset, test

if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"Using device: {device}")

def prune_weights(model, threshold):
    """
    Prunes the weights of a model by setting small weights to zero.

    Args:
        model (torch.nn.Module): The model to prune.
        threshold (float): The threshold value. Weights below this value will be pruned.

    Returns:
        torch.nn.Module: The pruned model.
    """
    with torch.no_grad():
        for name, param in model.named_parameters():
            if 'weight' in name:
                mask = torch.abs(param) > threshold
                param.mul_(mask)
    return model

def time_process(fn, *args):
    """
    Measures the time taken to execute a function and returns the elapsed time.
    """
    start = time.perf_counter()
    fn(*args)
    end = time.perf_counter()
    print(f"Time elapsed: {end - start:.2f}s")
    return end - start

def model_prune():
    """
    Prune the trained LSTMRegressor model and save the pruned model.
    """
    batch_size = 1
    model = LSTMRegressor(2, batch_size, num_layers=2)
    model.load_state_dict(torch.load(f"Model/model/LSTMRegressor_40.pth"))
    model.eval().to(device)
    dataset = SerialRNNDataset(lookback=40, group_num=[2, 3])
    _, test_loader = prep_dataset(dataset, batch_size, test_size=0.99)
    num_test = len(test_loader.dataset)

    time_used = time_process(test, model, test_loader, "test", "regression")
    print(f"Time used for 1 round of inference: {time_used/num_test:.3g}s")

    model = prune_weights(model, 0.01)

    time_used = time_process(test, model, test_loader, "test", "regression")
    print(f"Time used for 1 round of inference: {time_used/num_test:.3g}s")

    torch.save(model.state_dict(), f"Model/model/LSTMRegressor_40_pruned.pth")

if __name__ == "__main__":
    model_prune()