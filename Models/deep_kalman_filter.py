import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Check if CUDA is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class RandomWalkDataset(Dataset):
    def __init__(self, num_samples=1000, seq_length=50, observation_dim=1):
        super().__init__()
        self.num_samples = num_samples
        self.seq_length = seq_length
        self.observation_dim = observation_dim

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        # Start with an initial price (could be random or fixed)
        initial_price = torch.zeros(self.observation_dim)
        # Generate a sequence of price changes
        random_steps = torch.randn(self.seq_length, self.observation_dim)
        # Simulate the price using a random walk
        price_series = torch.cumsum(torch.cat([initial_price.unsqueeze(0), random_steps]), dim=0)
        # Return the (input, target) pair
        return price_series[:-1], price_series[1:]

class DeepKalmanFilter(nn.Module):
    def __init__(self, state_dim, observation_dim, hidden_dim):
        super(DeepKalmanFilter, self).__init__()
        self.state_dim = state_dim
        self.observation_dim = observation_dim
        self.hidden_dim = hidden_dim

        # Transition model parameters
        self.transition_matrix = nn.Parameter(torch.randn(state_dim, state_dim))
        self.transition_noise = nn.Parameter(torch.randn(state_dim, state_dim))

        # Observation model parameters
        self.observation_matrix = nn.Parameter(torch.randn(observation_dim, state_dim))
        self.observation_noise = nn.Parameter(torch.randn(observation_dim, observation_dim))

        # Nonlinear state and observation models
        self.state_model = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, state_dim)
        )
        
        self.observation_model = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, observation_dim)
        )

    def forward(self, observations):
        batch_size = observations.size(0)
        
        # Initialize hidden states
        hidden_state = torch.zeros(self.state_dim).to(observations.device)
        state_covariance = torch.eye(self.state_dim).to(observations.device)
        
        predicted_states = []
        predicted_observations = []
        
        for t in range(observations.size(1)):  # assuming observations is (batch, time, features)
            # Predict next state
            predicted_state = self.state_model(hidden_state)
            state_covariance = self.transition_matrix @ state_covariance @ self.transition_matrix.T + self.transition_noise
            
            # Predict observation
            predicted_observation = self.observation_model(predicted_state)
            observation_covariance = self.observation_matrix @ state_covariance @ self.observation_matrix.T + self.observation_noise
            
            # Kalman Gain
            kalman_gain = state_covariance @ self.observation_matrix.T @ torch.inverse(observation_covariance)
            
            # Update step
            observation_residual = observations[:, t, :] - predicted_observation
            hidden_state = predicted_state + kalman_gain @ observation_residual
            state_covariance = (torch.eye(self.state_dim).to(observations.device) - kalman_gain @ self.observation_matrix) @ state_covariance
            
            # Store predictions
            predicted_states.append(predicted_state.unsqueeze(1))
            predicted_observations.append(predicted_observation.unsqueeze(1))
        
        # Concatenate predictions along time dimension
        predicted_states = torch.cat(predicted_states, dim=1)
        predicted_observations = torch.cat(predicted_observations, dim=1)
        
        return predicted_states, predicted_observations
    
    def predict(self, hidden_state, state_covariance):
        # Predict next state
        predicted_state = self.state_model(hidden_state)
        
        # Predict the next state covariance matrix
        state_covariance_pred = self.transition_matrix @ state_covariance @ self.transition_matrix.T + self.transition_noise
        
        return predicted_state, state_covariance_pred

    def update(self, predicted_state, state_covariance, observation):
        predicted_observation = self.observation_model(predicted_state)
        
        # Observation covariance
        observation_covariance = self.observation_matrix @ state_covariance @ self.observation_matrix.T + self.observation_noise
        
        # Kalman Gain
        kalman_gain = state_covariance @ self.observation_matrix.T @ torch.inverse(observation_covariance)
        
        # Observation residual
        observation_residual = observation - predicted_observation
        
        # Update state
        updated_state = predicted_state + kalman_gain @ observation_residual
        
        # Update state covariance
        identity_matrix = torch.eye(self.state_dim).to(state_covariance.device)
        updated_state_covariance = (identity_matrix - kalman_gain @ self.observation_matrix) @ state_covariance
        
        return updated_state, updated_state_covariance


# Instantiate the DKF
state_dim = 4
observation_dim = 2
hidden_dim = 16
dkf = DeepKalmanFilter(state_dim, observation_dim, hidden_dim)


# Create the dataset
dataset = RandomWalkDataset(num_samples=1000, seq_length=50, observation_dim=1)

# Use DataLoader to handle batching
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Loss function and optimizer
criterion = torch.nn.MSELoss()
optimizer = optim.Adam(dkf.parameters(), lr=0.01)


# Training loop
num_epochs = 5
dkf.train()
for epoch in range(num_epochs):
    for batch_idx, (input_series, target_series) in enumerate(dataloader):
        input_series = input_series.to(device)
        target_series = target_series.to(device)
        
        optimizer.zero_grad()
        
        # Initial state
        hidden_state = torch.zeros(dkf.state_dim, device=device)
        state_covariance = torch.eye(dkf.state_dim, device=device)
        
        # Accumulate losses for each time step
        total_loss = 0
        for t in range(input_series.size(1)):
            # Perform prediction step
            predicted_state, state_covariance_pred = dkf.predict(hidden_state, state_covariance)
            
            # Get the actual observation at the current time step
            current_observation = input_series[:, t, :]
            
            # Perform update step
            updated_state, updated_state_covariance = dkf.update(predicted_state, state_covariance_pred, current_observation)
            
            # Compute the loss
            predicted_observation = dkf.observation_model(updated_state)
            loss = criterion(predicted_observation, target_series[:, t, :])
            total_loss += loss
            
            # Prepare for the next iteration
            hidden_state = updated_state
            state_covariance = updated_state_covariance
        
        # Backward pass
        total_loss.backward()
        optimizer.step()
        
        if batch_idx % 10 == 0:
            print(f'Epoch {epoch+1}, Batch {batch_idx+1}, Loss: {total_loss.item():.4f}')

print('Training complete')

