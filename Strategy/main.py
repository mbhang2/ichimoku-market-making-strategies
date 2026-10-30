import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
from tabulate import tabulate
import utility.candlestick as candlestick
import utility.data_parser as dp
import backtest.backtest as backtest
import backtest.trade_times_plot as ttp
import os
import sys

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(dir))

from Strategy.algorithm import ichimoku

# pd.set_option('display.max_rows', None)

ticker = "QQQ"
capital = 1000000
position_size_per_trade = 10  # in percent

ichimoku_length_option = 2
ichimoku_length = [[9, 26, 52], [7, 21, 42], [5, 13, 26]]
short = ichimoku_length[ichimoku_length_option][0]
mid = ichimoku_length[ichimoku_length_option][1]
long = ichimoku_length[ichimoku_length_option][2]

order_offset_list = [3, 5, 7]
position_size_per_trade_list = [3, 5, 10]

# cd = candlestick.candlestick_with_bbo(ticker, "20191001", "20191101")
# cd.to_csv(f"./Strategy/Sample_Data/IEX/{ticker}.csv")

# cd = pd.read_csv(f"./Strategy/Sample_Data/IEX/{ticker}.csv", converters={"Time": dp.to_timestamp})

"""
Backtest
"""
# result_df = backtest.run_backtest_no_stop_loss(cd, capital=capital, position_size_per_trade=position_size_per_trade, short=3, mid = 7, long=14, order_offset = 7, stop_loss_tick=3)

# result_df.to_csv(f"./Strategy/Sample_Data/IEX/{ticker}_trades.csv")

# """ 
# Algorithmic Trading Test
# """
# # # result = ichimoku.ichimoku_simple_bl_cl_cross_strategy(cd, 7, 21, 42, capital=capital, position_size_per_trade=position_size_per_trade)
# # # # # result = ichimoku.ichimoku_ls_bl_cross_strategy(cd, short, mid, long, capital=capital, position_size_per_trade=position_size_per_trade)
# # # # # result = ichimoku.ichimoku_cloud_shift_strategy(cd, short, mid, long, capital=capital, position_size_per_trade=position_size_per_trade)


# """
# Trading Stats
# """
# # # print(tabulate(combined_df, headers = 'keys', tablefmt = 'psql'))
# if len(result_df) == 0:
#     print("\nNO TRADES WERE MADE\n")

# else:
#     print("\n====================\nBacktest Result:\n")
#     print(f"Number of Trades: {len(result_df)}")
#     print(f"P&L Percent: {round((result_df['Equity'][len(result_df)-1]-capital)*100/capital, 2)}%")
#     print(f"Win Rate: {round(len(result_df.loc[result_df['P&L'] > 0])*100/len(result_df),2)}%")
#     print(f"P&L Ratio: {-round(result_df.loc[result_df['P&L']>0]['P&L'].mean()/result_df.loc[result_df['P&L']<0]['P&L'].mean(),2)}")
#     print(f"Average Profit Percent: {round(result_df.loc[result_df['P&L percent'] > 0]['P&L percent'].mean(), 2)}%")
#     print(f"Average Loss Percent: {round(result_df.loc[result_df['P&L percent'] < 0]['P&L percent'].mean(), 2)}%")
#     print(f"Max Drawdown: {np.min(round((result_df['Equity'].min()-capital)*100/capital, 2), 0)}%")
#     print("\n====================")

#     """
#     Plot
#     """
#     plt.plot((result_df["Equity"]-capital)*100/capital)
#     plt.title("Cumulative P&L")
#     plt.xlabel("Trades")
#     plt.ylabel("P&L "+"("+"%"+")")
#     plt.show()

print(ichimoku.compute_ichimoku(candlestick.candlestick("SPY", "20230103", "20230103"), 9, 26, 52))