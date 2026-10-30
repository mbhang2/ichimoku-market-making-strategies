import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import algorithmic_trading
import correlation
import file_parser
import time_based_execution


"""
Pair Correlation
"""
# df = correlation.pair_correlation("PSQ", "QQQ", "20191001", round=3)
# print(f"\nCorrelation coefficient between PSQ and QQQ is {df}\n")

# df = correlation.pair_correlation("SPY", "QQQ", "20191001", round=3)
# print(f"Correlation coefficient between SPY and QQQ is {df}\n")

# df = correlation.pair_correlation("GOOG", "GOOGL", "20191001")
# print(f"Correlation coefficient between GOOG and GOOGL is {df}\n")

"""
Multiple Correlation
"""

# df = correlation.multiple_correlation("20191001", "AAPL", "AMZN", "SPY", "QQQ", "TLT", "PSQ", "SDS")
# print(df)

"""
TLCC
"""
# window = 5*(10**9) # one way window
# increment = 1*(10**9)

# df = correlation.pair_TLCC("GOOG", "GOOGL", "20191001", increment=increment, window=window)
# print(df.max())

# plt.plot(df["Correlation coefficient"])
# plt.xlabel("Offset")
# plt.ylabel("Correlation coefficient")
# plt.show()

"""
Algorithmic Trading
"""
# algorithmic_trading.moving_average_strategy("QQQ", "20191001", 9, 21)
algorithmic_trading.multi_day_moving_average_strategy("QQQ", "20191001", "20191031", 9, 26)

"""
Time Based Execution
"""
# b = time_based_execution.time_based_change("SPY", "20191001", "20191030", precision=3)[0]
# s = time_based_execution.time_based_change("SPY", "20191001", "20191030", precision=3)[1]

# mb = max(b, key=b.get)
# ms = max(s, key=s.get)

# print(f"Best buying opportunity time: {mb} \nFrequency: {b[mb]}")
# print(f"Best selling opportunity time: {ms} \nFrequency: {s[ms]}")


