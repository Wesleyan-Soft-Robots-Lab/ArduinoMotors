import numpy as np
import time, tracemalloc


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def lstm_cell(
    x: np.ndarray,
    h: np.ndarray,
    c: np.ndarray,
    W_ih: np.ndarray,
    W_hh: np.ndarray,
    b_h: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Perform a single step of the LSTM cell.

    Args:
        x (numpy.ndarray): Input tensor of shape (batch_size, input_size).
        hidden (tuple): Tuple containing the previous hidden state (h) and cell state (c).
        W_ih (numpy.ndarray): Input-to-hidden weight matrix of shape (hidden_size, input_size).
        W_hh (numpy.ndarray): Hidden-to-hidden weight matrix of shape (hidden_size, hidden_size).
        b_h (numpy.ndarray): Hidden-to-hidden bias vector of shape (hidden_size,).

    Returns:
        tuple: Tuple containing the updated hidden state (h) and cell state (c).
    """
    gates = np.dot(W_ih, x) + np.dot(W_hh, h) + b_h
    i, f, g, o = np.split(gates, 4)
    i = sigmoid(i)
    f = sigmoid(f)
    g = np.tanh(g)
    o = sigmoid(o)
    c = f * c + i * g
    h = o * np.tanh(c)
    return h, c


def lstm_matrix_inference(
    W_xh: list[np.ndarray], W_hh: np.ndarray, b_h: np.ndarray, batch_size: int
):
    """
    Create a function that performs forward pass through LSTM layers.

    Args:
        W_xh (list[np.ndarray]): List of weight matrices for input-to-hidden connections for each LSTM layer.
        W_hh (np.ndarray): Weight matrix for hidden-to-hidden connections.
        b_h (np.ndarray): Bias vector for hidden-to-hidden connections.
        batch_size (int): Batch size.

    Returns:
        function: A function that performs forward pass through LSTM layers.
    """
    num_layers = len(W_xh)
    hidden_size = W_hh.shape[-1]

    def forward(x: np.ndarray) -> np.ndarray:
        """
        Perform forward pass through the LSTM layers.

        Args:
            x (np.ndarray): Input sequence of shape (seq_len, input_size).

        Returns:
            np.ndarray: Output hidden state of the last LSTM layer.
        """
        hidden = np.zeros((num_layers, hidden_size))
        cell = np.zeros((num_layers, hidden_size))
        seq_len = x.shape[0]
        for t in range(seq_len):
            hidden[0], cell[0] = lstm_cell(x[t], hidden[0], cell[0], W_xh[0], W_hh[0], b_h[0])
            hidden[1], cell[1] = lstm_cell(hidden[0], hidden[1], cell[1], W_xh[1], W_hh[1], b_h[1])
        return hidden[1]

    return forward


def fc_matrix_inference(W: np.ndarray, b: np.ndarray):
    """
    Create a function for performing forward inference using the fully connected matrix operation.

    Args:
        W (np.ndarray): The weight matrix of shape (n_outputs, n_features).
        b (np.ndarray): The bias vector of shape (n_outputs,).

    Returns:
        function: A function that performs the forward inference operation.
    """
    def forward(input_):
        """
        Perform forward inference using the fully connected matrix operation.

        Args:
            input_ (np.ndarray): The input data of shape (batch_size, n_features).

        Returns:
            np.ndarray: The output of the forward inference operation of shape (batch_size, n_outputs).
        """
        return np.dot(W, input_) + b

    return forward


def npiter(arr: np.ndarray):
    """
    Iterate over a numpy array.

    Args:
        arr (np.ndarray): The input numpy array.
    """
    for i in arr:
        yield i

def read_model_weights():
    weights = np.load("Model/matrix_form/LSTMRegressor.npy")
    W_hh = weights["W_hh"].squeeze()
    b_h = weights["b_h"].squeeze()
    W = weights["W"].squeeze()
    b = weights["b"].squeeze()
    W_xh = []
    for i in range(W_hh.shape[0]):
        W_xh.append(weights[f"W_xh_{i}"].squeeze())
        
    print([i.shape for i in W_xh], W_hh.shape, b_h.shape, W.shape, b.shape)

    return W_xh, W_hh, b_h, W, b

def lstm_inference(length, iterator):

    W_xh, W_hh, b_h, W, b = read_model_weights()

    batch_size = 1

    lstm_forward = lstm_matrix_inference(W_xh, W_hh, b_h, batch_size)
    fc_forward = fc_matrix_inference(W, b)

    output = np.zeros((length))
    start_time = time.perf_counter()
    for i, x in enumerate(iterator):
        output[i] = fc_forward(lstm_forward(x))
    end_time = time.perf_counter()

    print(f"Time taken for inference: {end_time - start_time:.6f} seconds")
    print((end_time - start_time) / length)
    return output

if __name__ == "__main__":
    test_array = np.load("Model/matrix_form/test_array.npy")
    target_array = np.loadtxt("Model/matrix_form/target_array.txt")
    length = test_array.shape[0]
    iterator = npiter(test_array)
    del test_array
    
    tracemalloc.start()
    output = lstm_inference(length, iterator)

    max_memory_usage = tracemalloc.get_traced_memory()[1]
    print(f"Maximum memory usage: {max_memory_usage / (1024):.2f} KB")

    tracemalloc.stop()

    print(output.shape, target_array.shape)
    from sklearn.metrics import r2_score # type: ignore
    r2 = r2_score(target_array, output)
    print(f"R2 Score: {r2}")
    for i in range(10):
        print(output[i], target_array[i])