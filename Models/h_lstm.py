import torch.nn as nn
import torch

# Check if CUDA is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class HierarchicalLSTM(nn.Module):
    def __init__(self, input_size, hidden_layer_size, output_size, num_layers):
        super(HierarchicalLSTM, self).__init__()
        self.hidden_layer_size = hidden_layer_size

        # Define the LSTM layers
        self.lstm1 = nn.LSTM(input_size, hidden_layer_size, batch_first=True)
        self.lstm2 = nn.LSTM(hidden_layer_size, hidden_layer_size, batch_first=True)

        # Define linear layers
        self.linear1 = nn.Linear(hidden_layer_size, hidden_layer_size)
        self.linear2 = nn.Linear(hidden_layer_size, output_size)

    def forward(self, input_seq):
        # Passing in the input and hidden state into the model and obtaining outputs
        lstm1_out, _ = self.lstm1(input_seq)
        # print(lstm1_out.shape)
        # You can consider taking the output of lstm1 and passing it through lstm2
        lstm2_out, _ = self.lstm2(lstm1_out)
        # print(lstm2_out.shape)
        # Get the last time step's output for the last batch for the next linear layer
        last_time_step = lstm2_out[:, :]

        # Passing through the first linear layer
        linear1_out = self.linear1(last_time_step)
        
        # Output from the final linear layer
        predictions = self.linear2(linear1_out)
        
        return predictions

    
        linear1_out = self.linear1(last_time_step)
        predictions = self.linear2(linear1_out)
    
        return predictions

# Assuming device is already defined as "cuda" or "cpu" based on CUDA availability
# Define hyperparameters
# input_size = 1  # for example, univariate time series
# hidden_layer_size = 50
# output_size = 1  # predicting one value ahead
# num_layers = 2  # number of stacked LSTM layers

# # Instantiate the model
# model = HierarchicalLSTM(input_size, hidden_layer_size, output_size, num_layers).to(device)


# # Loss function and optimizer
# criterion = nn.MSELoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# # Training loop
# model.train()
# for epoch in range(epochs):
#     for i in range(0, num_samples):
#         # Get the current batch of input data and targets
#         inputs = X[i:i+1]  # Adding batch dimension
#         targets = y[i:i+1]
        
#         # Zero the gradients
#         optimizer.zero_grad()
        
#         # Forward pass
#         output = model(inputs)
        
#         # Compute the loss
#         loss = criterion(output, targets)
        
#         # Backward pass and optimize
#         loss.backward()
#         optimizer.step()
    
#     print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

# print("Training complete")
