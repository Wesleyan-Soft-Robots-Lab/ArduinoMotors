import sys
import numpy as np
import torch
from typing import Callable

sys.path.append(".")
from Model.model import LSTMRegressor  # type: ignore
from Model.dataset import SerialRNNDataset  # type: ignore
from Model.train import prep_dataset, test
from Model.matrix_form.lstm_inference import *


def LSTM_extraction(
    lstm_layer: torch.nn.LSTM,
) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    """
    Extracts the weights and biases from the given RNN layer and returns them.

    Args:
        rnn_layer (torch.nn.RNN): The RNN layer from which to extract the weights and biases.

    Returns:
        list[np.ndarray]: The input-hidden weights of the RNN layer.
        np.ndarray: The hidden-hidden weights of the RNN layer.
        np.ndarray: The hidden biases of the RNN layer.
    """

    num_layers = lstm_layer.num_layers
    W_xh = []
    W_hh = []
    b_h = []

    for i in range(num_layers):
        W_xh.append(lstm_layer.__getattr__(f"weight_ih_l{i}").data)
        W_hh.append(lstm_layer.__getattr__(f"weight_hh_l{i}").data)
        b_h.append(
            lstm_layer.__getattr__(f"bias_ih_l{i}").data
            + lstm_layer.__getattr__(f"bias_hh_l{i}").data
        )

    for i in range(num_layers):
        W_xh[i] = W_xh[i].numpy()

    return W_xh, np.array(W_hh), np.array(b_h)


def FC_extraction(fc_layer: torch.nn.Linear) -> tuple[np.ndarray, np.ndarray]:
    """
    Extracts the weight and bias from a fully connected (FC) layer.

    Args:
        fc_layer (torch.nn.Linear): The fully connected layer.

    Returns:
        np.ndarray: The weight matrix of the FC layer.
        np.ndarray: The bias vector of the FC layer.
    """

    W = fc_layer.weight.data
    b = fc_layer.bias.data

    return np.array(W), np.array(b)


def dataset_to_numpy(dataloader) -> tuple[np.ndarray, np.ndarray]:
    batches = []
    targets = []
    for data, target in dataloader:
        batches.append(data.numpy())
        targets.append(target.numpy())
    return np.concatenate(batches), np.concatenate(targets)


def write_LSTMRegressor_weights(W_xh, W_hh, b_h, W, b):
    with open("Model/matrix_form/LSTMRegressorWeights.txt", "w") as file:
        for i in range(W_hh.shape[0]):
            for j in range(W_hh.shape[1]):
                print(
                    np.array2string(
                        W_hh[i, j],
                        separator=",",
                        max_line_width=1000,
                        formatter={"float_kind": lambda x: "%.6f" % x},
                    )[1:-1],
                    file=file,
                )
        for i in range(b_h.shape[0]):
            print(
                np.array2string(
                    b_h[i],
                    separator=",",
                    max_line_width=1000,
                    formatter={"float_kind": lambda x: "%.6f" % x},
                )[1:-1],
                file=file,
            )
        print(
            np.array2string(
                W[0], separator=",", max_line_width=1000, formatter={"float_kind": lambda x: "%.6f" % x}
            )[1:-1],
            file=file,
        )
        print(
            np.array2string(
                b, separator=",", max_line_width=1000, formatter={"float_kind": lambda x: "%.6f" % x}
            )[1:-1],
            file=file,
        )
        for i in range(len(W_xh)):
            for j in range(W_xh[i].shape[0]):
                print(
                    np.array2string(
                        W_xh[i][j],
                        separator=",",
                        max_line_width=1000,
                        formatter={"float_kind": lambda x: "%.6f" % x},
                    )[1:-1],
                    file=file,
                )
            

def main_comp():
    batch_size = 1
    model = LSTMRegressor(2, batch_size, num_layers=2)
    model.load_state_dict(
        torch.load(
            f"Model/model/LSTMRegressor_40.pth", map_location=torch.device("cuda")
        )
    )
    dataset = SerialRNNDataset(lookback=40, group_num=[2, 3])
    _, test_loader = prep_dataset(dataset, batch_size, test_size=0.99)
    test_array, target_array = dataset_to_numpy(test_loader)
    print(test_array.shape)
    np.save("Model/matrix_form/test_array.npy", test_array)
    np.savetxt(
        "Model/matrix_form/test_array.txt",
        test_array.reshape(-1, 2),
        delimiter=",",
        fmt="%.6f",
    )
    np.savetxt(
        "Model/matrix_form/target_array.txt",
        target_array,
        delimiter=",",
        fmt="%.6f",
    )

    W_xh, W_hh, b_h = LSTM_extraction(model.lstm)
    W, b = FC_extraction(model.fc)
    print([i.shape for i in W_xh], W_hh.shape, b_h.shape, W.shape, b.shape)

    structured_data = np.zeros(
        1,
        dtype=[
            ("W_hh", "f4", W_hh.shape),
            ("b_h", "f4", b_h.shape),
            ("W", "f4", W.shape),
            ("b", "f4", b.shape),
            *[(f"W_xh_{i}", "f4", W_xh[i].shape) for i in range(len(W_xh))],
        ],
    )
    structured_data["W_hh"] = W_hh
    structured_data["b_h"] = b_h
    structured_data["W"] = W
    structured_data["b"] = b
    for i in range(len(W_xh)):
        structured_data[f"W_xh_{i}"] = W_xh[i]

    np.save("Model/matrix_form/LSTMRegressor.npy", structured_data)

    write_LSTMRegressor_weights(W_xh, W_hh, b_h, W, b)


    output = np.zeros((test_array.shape[0]))
    lstm_forward = lstm_matrix_inference(W_xh, W_hh, b_h, batch_size)
    fc_forward = fc_matrix_inference(W, b)
    model.eval().to('cuda')
    model_output = np.zeros((test_array.shape[0]))
    for i in range(test_array.shape[0]):
        output[i] = fc_forward(lstm_forward(test_array[i]))
        model_output[i] = model(torch.tensor([test_array[i]]).to('cuda', torch.float32)).item()
    for i in range(10):
        print(output[i], model_output[i])


if __name__ == "__main__":

    main_comp()
