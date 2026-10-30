#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 02:52:04 2023

@author: akshay
"""

from ..Models.h_lstm import HierarchicalLSTM
from ..Training.model_1_lstm import *
import os
import torch
import torch.nn as nn
import pandas as pd
from torch.utils.data import DataLoader, TensorDataset, Subset

folder_name = 'group_02_project'

# Check if CUDA is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class lstm_to_trade():
    def __init__(self, forward_predictions = 1, search_path = '/home', hidden_layer_size = 50 , num_layers = 2, lr = 0.0005):
        self.forward_predictions = forward_predictions
        self.search_path = search_path
        self.hidden_layer_size = hidden_layer_size
        self.num_layers = num_layers
        self.lr = lr
    
    def data_processing(self):
    
        start_path = os.path.expanduser(self.search_path)  # Start search from the user's home directory
        folder_path = find_folder(folder_name, start_path)
        df = pd.read_csv(f'{folder_path}/Polygon_API/polygon_data/TRADE_SPY_20230104_000000_to_20230104_235959.csv')
    
        df = df_v_1(df)
        
        # Create a DataFrame from the split values
        split_values = df['conditions'].str.split(';', expand=True).stack().reset_index(level=1, drop=True)
        
        # Use get_dummies for one-hot encoding
        one_hot_encoded = pd.get_dummies(split_values, dtype=int).groupby(level=0).max()
        
        # Join with the original DataFrame
        df = df.join(one_hot_encoded)
        
        # Fill NaNs with 0s for only the new columns
        new_columns = one_hot_encoded.columns
        df[new_columns] = df[new_columns].fillna(0)
        
        new_columns = []
        n = self.forward_predictions
        for i in range(1, n + 1):
            column_name = f'normalized_price_{i}'
            df[column_name] = df['normalized_price'].shift(-i)
            new_columns.append(column_name)
        
        # Forward filling the NaN values only in the new columns
        df[new_columns] = df[new_columns].ffill()

        # Select features and target
        columns = list(df.columns[df.columns.get_loc('normalized_size'):])
        features = df.loc[:, columns]# Add other relevant features
        #AP: Change target as a dynamic variable with multiple columns 
        # to match multiple outputs: Still to do
        target = df.loc[:, ['normalized_price'] + new_columns]  # Replace with your target variable
        print(features.shape)
        print(target.shape)

        return [features, target]
    
    def prepare_for_training(self):
        features, target = self.data_processing()
        # Convert to PyTorch tensors
        features_tensor = torch.tensor(features.values, dtype=torch.float32)
        target_tensor = torch.tensor(target.values, dtype=torch.float32)
        print(features_tensor.shape)
        print(target_tensor.shape)

        # Create dataset and data loader
        dataset = TensorDataset(features_tensor, target_tensor)
        
        return [features, dataset]

    def model_setup(self):
        features, _ = self.prepare_for_training()
        # Initialize the model
        input_size = features.shape[1]
        output_size = self.forward_predictions + 1
        model = HierarchicalLSTM(input_size, self.hidden_layer_size, output_size, self.num_layers)
        model.to(device)

        # Loss function and optimizer
        # criterion = nn.MSELoss()
        criterion = self.loss_with_windowed_trend
        optimizer = torch.optim.Adam(model.parameters(), lr= self.lr)
        
        return [model, criterion, optimizer]

    def train_val_test_split(self, train_ratio = 0.7, val_ratio = 0.15):
        _, dataset = self.prepare_for_training()
        # Assuming 'dataset' is your complete time-ordered dataset
        train_size = int(train_ratio * len(dataset))
        val_size = int(val_ratio * len(dataset))

        # Sequential split
        train_dataset = Subset(dataset, range(0, train_size))
        val_dataset = Subset(dataset, range(train_size, train_size + val_size))
        test_dataset = Subset(dataset, range(train_size + val_size, len(dataset)))

        train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=False)
        val_dataloader = DataLoader(val_dataset, batch_size=32, shuffle=False)
        test_dataloader = DataLoader(test_dataset, batch_size=32, shuffle=False)

        return [train_dataloader, val_dataloader, test_dataloader]
    
    def loss_with_windowed_trend(self, y_true, y_pred):
        
        mse = torch.nn.functional.mse_loss(y_pred, y_true)

        # Trend penalty initialization
        trend_penalty = 0.0

        length = y_true.size(0)

        for i in range(length - self.forward_predictions):
            trend_true = torch.sign(y_true[i + 1:i + 1 + self.forward_predictions] - y_true[i])
            trend_pred = torch.sign(y_pred[i + 1:i + 1 + self.forward_predictions] - y_pred[i])

            # Compute trend difference
            trend_difference = torch.square(trend_true - trend_pred)

            # Accumulate trend penalty
            trend_penalty += torch.mean(trend_difference)

        # Normalize the trend penalty by the number of elements
        trend_penalty /= (length - self.forward_predictions)

        # Total loss with trend penalty
        return mse + 0.5 * trend_penalty

    def run_model(self, patience = 10):
        # Early stopping parameters
        patience = patience  # number of epochs to wait for improvement before stopping
        best_loss = float('inf')
        epochs_no_improve = 0
        
        model, criterion, optimizer = self.model_setup()
        train_dataloader, val_dataloader, test_dataloader = self.train_val_test_split()
        for epoch in range(100):  # 100 epochs
            train_loss, val_loss = 0, 0
            model.train()
            for inputs, targets in train_dataloader:
                inputs, targets = inputs.to(device), targets.to(device)
                # ... Training steps
                # Forward pass
                predictions = model(inputs)
                #loss = criterion(predictions, targets)
                loss = self.loss_with_windowed_trend(targets, predictions)
                #train_loss += criterion(predictions, targets).item()
                train_loss += loss.item()
                # Backward pass and optimize
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            # print(f'Epoch {epoch+1}, Loss: {loss.item()}')
            train_loss /= len(train_dataloader)
            model.eval()
            val_loss = 0
            with torch.no_grad():
                for inputs, targets in val_dataloader:
                    inputs, targets = inputs.to(device), targets.to(device)
                    predictions = model(inputs)
                    #val_loss += criterion(predictions, targets).item()
                    val_loss += self.loss_with_windowed_trend(targets, predictions).item()
                    
    
            val_loss /= len(val_dataloader)
            print(f'Epoch {epoch+1}, Training Loss: {train_loss}, Validation Loss: {val_loss}')
    
            # Early stopping check
            if val_loss < best_loss:
                best_loss = val_loss
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1
                if epochs_no_improve == patience:
                    print(f'Stopping early at epoch {epoch+1}')
                    break
    
        # Evaluate on test set after training is complete
        model.eval()
        test_loss = 0
        with torch.no_grad():
            for inputs, targets in test_dataloader:
                inputs, targets = inputs.to(device), targets.to(device)
                predictions = model(inputs)
                #test_loss += criterion(predictions, targets).item()
                test_loss += self.loss_with_windowed_trend(targets, predictions).item()
                
        test_loss /= len(test_dataloader)
        print(f'Test Loss: {test_loss}')
    
        torch.save(model.state_dict(), 'model_h_lstm.pth')
        return predictions

lt = lstm_to_trade(5, '/home/lux')
predictions = lt.run_model()

# Training loop
# for epoch in range(100):  # 10 epochs
#     for inputs, targets in dataloader:
#         inputs, targets = inputs.to(device), targets.to(device)

#         # Forward pass
#         predictions = model(inputs)
#         loss = criterion(predictions, targets)

#         # Backward pass and optimize
#         optimizer.zero_grad()
#         loss.backward()
#         optimizer.step()

#     print(f'Epoch {epoch+1}, Loss: {loss.item()}')
