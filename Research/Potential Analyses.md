[WIP]
## Data Needed: 
	1. Order book data
	2. Tick data (IEX)
	3.  Level II data with details about orders, bid-ask spreads, and market orders

### Tick Data
1. Descriptive statistics for each symbol 
2. Time series analysis (autocorrelation to identify potential lagged relationships)
	- Positive ACF = momentum
	- Negative ACF = mean-reverting
	- This is best done with stationary data ... so maybe aggregate instead of raw tick?
```
from statsmodels.graphics.tsaplots import plot_acf
import matplotlib.pyplot as plt

# using tick data price for a symbol.
plot_acf(tick['price'])
```
3. Rolling statistics like moving averages (5 mins, 10 mins for tick data), exponential moving averages, Bollinger Bands (need to look more into these).
4. Use rolling standard deviation to calculate historical volatility.

#### Aggregated Tick Data (1 or 5 minute data)
1. Generalized Autoregressive Conditional Heteroskedasticity (GARCH) models used for predicting future volatility (arch/statsmodel) 
	*  (HFGARCH might be more appropriate for tick data... further research.)
2. Relative Strength Index, Moving Average Convergence Divergence, and Stochastic Oscillator 
3. Chart Pattern Recognition (use ta library)
	- [TODO]: Read into this for Lux

### Further Analyses with Other Data

1. Plot order book depth over time
2. Plot bid-ask spread over time to see changes in response to events
3. Calculate volume of market orders and examine impact on order book dynamics
4. Monitor order book imbalance and impact on prices
5. Examine order book depth at different price levels to determine liquidity
		- bid-ask volume imbalance
### Some Resources:

* Russell & Engle (2010): Analysis of High Frequency Data

