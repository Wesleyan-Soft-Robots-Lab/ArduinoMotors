import os, sys
import pandas as pd
import numpy as np
import re
import torch
import pickle
from torch.utils.data import Dataset
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split # type: ignore

sys.path.append('.')
from preprocess.prep_data import combine_files

class BaseDataset(Dataset):
    def __init__(self) -> None:
        super().__init__()
        self.input = [] # type: list
        self.labels = [] # type: list
        self.train_set: list | None = None
        self.test_set: list | None = None
    
    def __len__(self) -> int:
        return len(self.input)
    
    def __getitem__(self, index):
        input, label = self.input[index], self.labels[index]
        input = torch.tensor(input, dtype=torch.float32)
        label = torch.tensor(label, dtype=torch.float32)

        return input, label
    
    def split(self, test_size: float = 1/3):
        pass

    def save(self, path: str):
        """
        Saves the dataset to a file.

        Args:
            path (str): The path to the file.
        """
        with open(path, 'wb') as f:
            pickle.dump(self, f)

class BaseDatasetforClassification(BaseDataset):
    def __init__(self) -> None:
        super().__init__()
    
    def split(self, test_size: float = 1/3, n_splits: int = 2):
        sss = StratifiedShuffleSplit(n_splits=n_splits,test_size=test_size)

        features = [sample for sample in self.input]
        features = (features - np.mean(features, axis=0)) / np.std(features, axis=0)
        labels = [sample for sample in self.labels] 

        print(features)

        for train_index, test_index in sss.split(features, labels):
            train_set = [self.input[i] for i in train_index]
            test_set = [self.input[i] for i in test_index]

        train_set.append((np.zeros(16, dtype='float32'), 0))
        # train_set.append((self.base, 0))

        self.train_set = train_set
        self.test_set = test_set
        
        return train_set, test_set


class BaseDatasetforRegression(BaseDataset):
    def __init__(self) -> None:
        super().__init__()

    def split(self, test_size: float = 1/3):
        self.train_set, self.test_set = train_test_split(list(zip(self.input, self.labels)), test_size=test_size)
        return self.train_set, self.test_set



class SerialRNNDataset(BaseDatasetforRegression):
    def __init__(self, lookback: int = 3):
        super().__init__()
        self.look_back = lookback
        all_data = combine_files()
        for df in all_data:
            for index, row in df.iterrows():
                if index < 50: continue
                # if all([df.at[index-i, 'E'] for i in range(lookback)]):
                if any(np.isnan(row[1])):
                    # print(index)
                    continue
                self.input.append(np.array([np.array(df.loc[index-i][0]) for i in range(lookback)]))
                self.labels.append(row[1])
                    # print(self.input[-1], self.labels[-1])
        
        self.input = np.array(self.input) # type: ignore
        self.labels = np.array(self.labels) # type: ignore
        # print(type(self.input))
        # print(self.labels)
        # self.input = (self.input - np.mean(self.input, axis=0))
        # print(np.mean(self.input, axis=0))
        # self.labels = self.labels / 90 # type: ignore
        self.input = torch.from_numpy(self.input).to(dtype=torch.float32)
        self.labels = torch.from_numpy(self.labels).to(dtype=torch.float32)

        # print(self.input.shape)

        # import matplotlib.pyplot as plt
        # plt.figure()
        # plt.plot(self.labels)
        # plt.figure()
        # plt.plot(self.input[:,0,0])
        # plt.figure()
        # plt.plot(self.input[:,0,1])
        # plt.show()


class RigDataset(BaseDatasetforClassification):
    def __init__(self, path: str) -> None:
            """
            Initializes a new instance of the Dataset class.

            Args:
                path (str): The path to the data file.

            Raises:
                Exception: If the number of sensors for a rig and round is not equal to 16.
            """
            super().__init__()
            self.input = []
            data = self.load_data(path)
            # print(data)
            self.labels = pd.unique(data['Model'])
            self.base = data.query('Model == "0"')['Resistance'].to_numpy().astype('float32')
            
            for deg in self.labels:
                deg_data = data.query(f'Model == "{deg}"')
                if deg == '0':
                    continue
                for round in pd.unique(deg_data['Round']):
                    tmp = deg_data.query(f'Round == {round}')['Resistance'].to_numpy(dtype='float32') - self.base
                    if len(tmp) != 16:
                        raise Exception(f'Incorrect number of sensors for rig {deg} deg, round {round}')
                    self.input.append((tmp, np.where(self.labels == deg)[0][0]))
            print('Dataset loaded')

            self.input = [np.array(sample[0]) for sample in self.input]
            self.labels = [sample[1] for sample in self.input]
    
    def __getitem__(self, index):
        input, label = self.input[index]
        input = torch.tensor(input, dtype=torch.float32)
        label = torch.tensor(label, dtype=torch.float32)

        return input, label
    
    def load_data(self, data_path: str):
        rig_list = os.listdir(data_path)
        try:
            rig_list.remove(".DS_Store")
        except:
            pass

        self.preprocess_data(data_path)

        rig_data = pd.DataFrame(columns=["Model", "Sensor", "Round", "Resistance"])
        
        for rig_dir in rig_list:
            angle = rig_dir.split(' ')[1]
            if angle == "0":
                num_round = 1
            else:
                num_round = 3
            print(f'Loading data for rig {angle} deg...')
            for sensor_id in range(1,17):
                for round in range(1,num_round+1):
                    tmp_data = pd.read_csv(os.path.join(data_path,rig_dir,f'on rig-{sensor_id:02}-round{round}.csv'))
                    tmp_resist = tmp_data['Resistance'].mean()
                    # print(tmp_resist)
                    rig_data = rig_data._append({
                        "Model": angle,
                        "Sensor": sensor_id,
                        "Round": round,
                        "Resistance": tmp_resist
                    }, ignore_index=True) # type: ignore
        
        return rig_data
    
    def preprocess_data(self, data_path: str):
        rig_list = os.listdir(data_path)
        try:
            rig_list.remove(".DS_Store")
        except:
            pass
        pattern = r'on rig-(\d+)-round(\d+).csv'

        print('Preprocessing data...')

        for dir in rig_list:
            files = os.listdir(os.path.join(data_path,dir))
            for file in files:
                if re.match(pattern, file):
                    df = pd.read_csv(os.path.join(data_path,dir,file))
                    if 'Resistance' != df.columns[2]:
                        new_head = df.columns.values.tolist()
                        new_head[2] = 'Resistance'
                        print(f'Change {df.columns[2]} to Resistance')
                        df.columns = new_head
                        df.to_csv(os.path.join(data_path,dir,file), index=False)
                    # print(df.columns)

if __name__ == "__main__":
    data_path = r'C:\Users\softrobotslab\ArduinoMotors\Training_data'
    data = RigDataset(data_path)
    data.split()
    data.save("Model/dataset/strap_dataset.pickle")
    print(data.input)
    print(train_test_split([1,2,3,4,5,6],[0.1,0.2,0.3,0.4,0.5,0.6], test_size=1/3))
    data = SerialRNNDataset()
    pass