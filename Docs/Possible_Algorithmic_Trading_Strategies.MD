#Algorithmic Trading Strategies
### 1. Moving Average Cross - Michael
Moving average cross is one of the most basic algorithmic trading strategy.Using two moving averages with different periods, trade is entered when the moving average orientation suggests a trend reversal. <br>
<br>
#### Buy Condition:
Shorter period moving average crosses over the longer period moving average.<br>
ㅤ
#### Sell Condition:
Shorter period moving average crosses under the longer period moving average. <Br>
ㅤ<br>
![Moving average cross example](../Images/Algorithmic%20Trading/MA_Cross.png)
ㅤ
### 2. Stochastic Oscillator
Stochastic is a momentum oscillator that quantifies the current close price relative to the high and low of a given period. Stochastic oscillator is composed of two lines: %K line that measures the relative level of the close price over the n-period, and %D line, a smoothing line of the %K line.
<br>
ㅤ
#### Buy Condition:
%K line crosses over the %D line<br>
ㅤ
#### Sell Condition:
%K line crosses below the %D line<br>
ㅤ<br>
![Stochastic oscillator example](../Images/Algorithmic%20Trading/Stochastic_Oscillator.png)

### 3. ON Balance Volume (OBV)
OBV is a volume indicator that assumes that the volume can be used to predict the price movement. OBV compares the current close with the previous close; if greater, add volume to the obv value, and vice versa (recursive). OBV also has a signal line, a moving average of the obv line.
<br>
#### Buy Condition:
OBV crosses over the signal line.<br>
ㅤ
#### Sell Condition:
OBV crosses below the signal line. <Br>
ㅤ<br>
![On balance volume example](../Images/Algorithmic%20Trading/OBV.png)

### 4. Ichimoku Cloud - Michael
Ichimoku cloud is a comprehensive indicator composed of 5 lines:
* Conversion line: average of the high and low of the 9-day period
* Base line: average of the high and low of the 26-day period
* Lagging span: Close price shifted 26 days backwards
* Leading span A: average of conversion and base line shifted 26 days to the future
* Leading span B: average of the high and low of the 52-day period shifted 26 days to the future
* Cloud: area between two leading spans
<br>
#### Buy Condition:
TBD<br>
ㅤ
#### Sell Condition:
TBD <Br>
ㅤ<br>
![Ichimoku example]()


### 5. Bollinger Bands
Bollinger band is a momentum indicator that is composed of three lines: moving average (20 period as default), upper and lower bands (2 standard deviation apart from the moving average as default).
<br>
#### Buy Condition:
TBD<br>
ㅤ
#### Sell Condition:
TBD <Br>
ㅤ<br>
![Bollinger bands example]()

