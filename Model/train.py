import sys
import numpy as np
import pandas as pd
import pickle
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import mean_squared_error, r2_score # type: ignore
import matplotlib.pyplot as plt # type: ignore
import concurrent.futures as cf
from tqdm import trange

sys.path.append(".")
from Model.model import *  # type: ignore
from Model.dataset import *  # type: ignore

if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"Using device: {device}")


def prep_dataset(dataset: BaseDataset, batch_size: int, test_size: float=1/3) -> tuple[DataLoader, DataLoader]: # type: ignore
    """
    Prepares the dataset for training and testing.

    Args:
        dataset (BaseDataset): The dataset to be split into train and test sets.
        batch_size (int): The batch size for the data loaders.
        test_size (float, optional): The proportion of the dataset to be used for testing. Defaults to 1/3.

    Returns:
        Tuple[DataLoader, DataLoader]: A tuple containing the train and test data loaders.
    """
    train_set, test_set = dataset.split(test_size=test_size)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader


def train(
    model: nn.Module,
    num_epoch: int,
    train_loader: DataLoader,
    test_loader: DataLoader,
    dataset: Dataset,
    save_name: str,
    train_type: str,
    show_plot: bool = True,
):
    """
    Trains the given model for the specified number of epochs.

    Args:
        model (nn.Module): The model to be trained.
        num_epoch (int): The number of epochs to train the model for.
        train_loader (DataLoader): The data loader for the training set.
        test_loader (DataLoader): The data loader for the test set.
        dataset (Dataset): The dataset used for training.
        save_name (str): The name of the file to save the model to.
        train_type (str): The type of training, either "classification" or "regression".
        show_plot (bool, optional): Whether to show the loss and accuracy plots. Defaults to True.

    Returns:
        nn.Module: The trained model.
        list: The list of loss values for each epoch.
        list: The list of accuracy values for each epoch.
    """
    try:
        model.to(device)
    except:
        print(f"Model not on device {device}")

    if train_type == "classification":
        criterion = nn.CrossEntropyLoss()
    elif train_type == "regression":
        criterion = nn.MSELoss() # type: ignore
        # criterion = nn.L1Loss() # type: ignore
    optimizer = optim.AdamW(model.parameters(), lr=0.0001)

    all_loss = []
    all_acc = []
    # for batch in train_loader:
    #     if torch.isnan(batch).any():
    #         print('Nan detected in input data')
    #         break
    print("Training model...")
    for epoch in trange(num_epoch):
        running_loss = 0.0
        for input, label in train_loader:
            input, label = input.to(device, dtype=torch.float32), label.to(device, dtype=torch.float32)

            optimizer.zero_grad()

            output = model(input)
            # print("input", input)
            # print("label", label)
            # print("output", output)
            # print(len(output))
            # print(len(label))
            loss = criterion(output, label)
            # fixed_value = 1.0
            # loss = torch.tensor(fixed_value, requires_grad=True, device=output.device)
            # print(loss)
            # print(input[:3, -2:, :], label[:3], output[:3])
            loss.backward()

            optimizer.step()

            running_loss += loss.item()
        # print(output[:3].detach().cpu().numpy()*90, label[:3].detach().cpu().numpy()*90)
        test(model, train_loader, "train", train_type)
        test_acc = test(model, test_loader, "test", train_type)
        all_acc.append(test_acc)

        print(f"\nEpoch {epoch+1} loss: {running_loss/len(train_loader)}")
        all_loss.append(running_loss/len(train_loader))

    print("\nFinished training, testing model...")
    test(model, test_loader, "test", train_type)

    torch.save(model.state_dict(), f"Model/model/{save_name}.pth")

    plt.figure()
    plt.title("Loss")
    plt.plot(all_loss)
    plt.savefig(f"Model/model/{save_name}_loss.png")
    plt.figure()
    plt.plot(all_acc)
    plt.title("Accuracy (Correlation)")
    plt.savefig(f"Model/model/{save_name}_acc.png")
    if show_plot:
        plt.show()


    return model, all_loss, all_acc


def test(model: nn.Module, test_loader: DataLoader, title: str, type: str):
    """
    Tests the given model on the test set.

    Args:
        model (nn.Module): The model to be tested.
        test_loader (DataLoader): The data loader for the test set.
        title (str): The title of the test set.
        type (str): The type of the test set, either "classification" or "regression".

    Returns:
        float: The evaluation metric (accuracy or R2 score) on the test set.
    """
    try:
        model.to(device)
    except:
        pass

    with torch.no_grad():
        corr = 0
        total = 0
        all_pred = torch.tensor([]).to(device)
        all_labels = torch.tensor([]).to(device)
        for input, label in test_loader:
            input, label = input.to(device, dtype=torch.float32), label.to(
                device, dtype=torch.float32
            )

            output = model(input)
            if type == "classification":
                _, pred = torch.max(output.data, dim=1)
                total += label.size(0)
                corr += (pred == label).sum().item()
            elif type == "regression":
                all_pred = torch.cat((all_pred, output))
                all_labels = torch.cat((all_labels, label))
        
        if type == "regression":
            # print('all labels: ',all_labels)
            # print('all pred: ',all_pred)
            r2 = r2_score(all_labels.cpu().numpy(), all_pred.cpu().numpy())
            print(f"R2 Score on {title} set: {r2}")
            return r2
        elif type == "classification":
            accuracy = 100 * corr / total
            print(f"Accuracy on {title} set: {accuracy}%")
            return accuracy

def model_test():
    """
    Test the trained LSTMRegressor model on different lookback values and plot the accuracy.
    """
    lookback = [5,10,15,20,25,30,35,40]
    all_acc = np.zeros(8)
    for i, lb in enumerate(lookback):
        model = LSTMRegressor(4, 16, num_layers=2)
        model.load_state_dict(torch.load(f"Model/model/LSTMRegressor_{lb}.pth"))
        model.eval()
        dataset = SerialRNNDataset(lookback=lb)
        _, test_loader = prep_dataset(dataset, 16, test_size=0.99)
        all_acc[i] = test(model, test_loader, "test", "regression")
    
    plt.figure()
    plt.plot(lookback, all_acc)
    plt.title("Accuracy")
    plt.savefig("Model/model/serial_acc.png")
    plt.show()


def train_rig_main():
    """
    Trains a model for pose estimation on the reading from the multimeter.
    """
    dataset_path = "Model/dataset/rig_dataset.pickle"
    dataset = pickle.load(open(dataset_path, "rb"))
    batch_size = 16
    train_loader, test_loader = prep_dataset(dataset, batch_size, test_size=0.2)
    model, save_name = LinearClassifier(batch_size), "LinearClassifier"
    # model, save_name = ConvClassifier(batch_size), 'ConvClassifier'
    model = train(model, 30, train_loader, test_loader, dataset, save_name)


def train_serial_main(lookback=42, num_epoch=5000):
    """
    Trains a model for pose estimation on the serial reading from Arduino.
    """
    dataset = SerialRNNDataset(lookback=lookback)
    batch_size = 32
    train_loader, test_loader = prep_dataset(dataset, batch_size)
    model, save_name = LSTMRegressor(input_size=4, batch_size=batch_size, num_layers=2, output_size=2), f"LSTMRegressor_strap_{lookback}"
    # model.load_state_dict(torch.load(f"Model/model/{save_name}.pth"))
    model, all_loss, all_acc = train(model, num_epoch, train_loader, test_loader, dataset, save_name, "regression", show_plot=True)

    return lookback, all_loss, all_acc

if __name__ == "__main__":
    # train_rig_main()
    # loss = np.zeros(8)
    # acc = np.zeros(8)
    # lookback = [5,10,15,20,25,30,35,40]
    # with cf.ProcessPoolExecutor(max_workers=4) as executor:
    #     results = executor.map(train_serial_main, lookback)
    #     for i, result in enumerate(results):
    #         loss[i] = result[1][-1]
    #         acc[i] = result[2][-1]


    train_serial_main()