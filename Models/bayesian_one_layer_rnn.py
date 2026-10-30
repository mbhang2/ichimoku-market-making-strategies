import torch
import torch.nn as nn
import pyro
from pyro.nn import PyroModule, PyroSample
from pyro.infer import SVI, Trace_ELBO
from pyro.optim import Adam
from pyro.distributions import Normal

# Define the Bayesian RNN model
class BayesianRNN(PyroModule):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.rnn = PyroModule[nn.RNN](input_size, hidden_size)
        self.rnn.weight_ih_l0 = PyroSample(prior=Normal(0., 1.).expand([hidden_size, input_size]).to_event(2))
        self.rnn.weight_hh_l0 = PyroSample(prior=Normal(0., 1.).expand([hidden_size, hidden_size]).to_event(2))

        self.fc = PyroModule[nn.Linear](hidden_size, output_size)
        self.fc.weight = PyroSample(prior=Normal(0., 1.).expand([output_size, hidden_size]).to_event(2))
        self.fc.bias = PyroSample(prior=Normal(0., 10.).expand([output_size]).to_event(1))

    def forward(self, x, h0=None):
        # Forward pass through RNN
        x, hn = self.rnn(x, h0)
        # Pass the output of the last time step to the fully connected layer
        x = self.fc(x[:, -1, :])
        return x

# Assuming you have some data in X_train (sequence data) and Y_train (target data)
# X_train should be shaped (batch_size, sequence_length, input_size)
# Y_train should be shaped (batch_size, output_size)

input_size = 1  # For example, for a univariate time series
hidden_size = 5
output_size = 1  # Predicting one value
bayesian_rnn = BayesianRNN(input_size, hidden_size, output_size)

# Guide function for variational inference (VI)
guide = pyro.infer.autoguide.AutoDiagonalNormal(bayesian_rnn)

# Training
optimizer = Adam({"lr": 0.01})
svi = SVI(bayesian_rnn, guide, optimizer, loss=Trace_ELBO())

num_iterations = 500
for j in range(num_iterations):
    loss = svi.step(X_train, Y_train)
    if j % 100 == 0:
        print(f"Epoch {j} : loss = {loss}")
