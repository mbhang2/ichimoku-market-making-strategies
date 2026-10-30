import torch
import torch.nn as nn
import torch.optim as optim

# Define the RNN model
class OnlineRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(OnlineRNN, self).__init__()
        self.rnn = nn.RNN(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x, hidden):
        # Forward pass through RNN
        out, hidden = self.rnn(x, hidden)
        # Pass the output of the last time step to the fully connected layer
        out = self.fc(out[:, -1, :])
        return out, hidden

# Assuming the following hyperparameters are defined
input_size = 1
hidden_size = 10
output_size = 1

# Initialize the RNN
model = OnlineRNN(input_size, hidden_size, output_size)

# Loss function and optimizer
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

data_stream = torch.randn(100, 1)  # 100 time steps, univariate

# Hidden state initialization
hidden = torch.zeros(1, 1, hidden_size)

# Online training loop
model.train()
for t in range(1, len(data_stream)):
    # Get the input and target from the current stream
    input = data_stream[t-1:t].unsqueeze(0).unsqueeze(0)  # Add batch and sequence dimension
    target = data_stream[t].unsqueeze(0).unsqueeze(0)  # Add batch and sequence dimension

    # Forward pass
    output, hidden = model(input, hidden)
    
    # Compute loss
    loss = criterion(output, target)
    
    # Zero the gradients
    optimizer.zero_grad()
    
    # Backward pass
    loss.backward()
    
    # Update parameters
    optimizer.step()
    
    # Detach the hidden state to prevent backpropagating through the entire stream
    hidden = hidden.detach()

    print(f'Time Step {t}: loss = {loss.item()}')

print('Online training complete')
