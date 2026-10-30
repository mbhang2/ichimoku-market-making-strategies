import torch
import torch.nn as nn
import pyro
from pyro.nn import PyroModule, PyroSample
from pyro.infer import SVI, Trace_ELBO
from pyro.optim import Adam
from pyro.distributions import Normal

class BayesianRNNLayer(PyroModule):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.rnn = PyroModule[nn.RNN](input_size, hidden_size, batch_first=True)
        self.rnn.weight_ih_l0 = PyroSample(prior=Normal(0., 1.).expand([hidden_size, input_size]).to_event(2))
        self.rnn.weight_hh_l0 = PyroSample(prior=Normal(0., 1.).expand([hidden_size, hidden_size]).to_event(2))

    def forward(self, x, h0=None):
        x, hn = self.rnn(x, h0)
        return x, hn

class BayesianRNN(PyroModule):
    def __init__(self, input_size, hidden_size, output_size, num_layers):
        super().__init__()
        self.num_layers = num_layers
        self.layers = nn.ModuleList([BayesianRNNLayer(input_size if i == 0 else hidden_size, hidden_size) for i in range(num_layers)])
        self.fc = PyroModule[nn.Linear](hidden_size, output_size)
        self.fc.weight = PyroSample(prior=Normal(0., 1.).expand([output_size, hidden_size]).to_event(2))
        self.fc.bias = PyroSample(prior=Normal(0., 10.).expand([output_size]).to_event(1))

    def forward(self, x, h0=None):
        # Forward pass through each layer in `self.layers`
        hn = h0
        for i, layer in enumerate(self.layers):
            x, hn = layer(x, hn)
        
        # Pass the output of the last time step of the last layer to the fully connected layer
        x = self.fc(x[:, -1, :])  # We only care about the last output
        return x

# Rest of the code for data preparation, guide, and training loop is similar

# Assuming you have defined X_train and Y_train

input_size = 1  # For a univariate time series
hidden_size = 5
output_size = 1  # Predicting one value
num_layers = 3
bayesian_rnn = BayesianRNN(input_size, hidden_size, output_size, num_layers)

# Guide function for variational inference (VI)
guide = pyro.infer.autoguide.AutoDiagonalNormal(bayesian_rnn)

# Training
optimizer = Adam({"lr": 0.01})
svi = SVI(bayesian_rnn, guide, optimizer, loss=Trace_ELBO())

num_iterations = 500
for j in range(num_iterations):
    loss = svi.step(X_train, Y_train)
    if j % 100 == 0:
        print(f"Epoch {j} : Loss = {loss}")
