import numpy as np
import os
import pandas as pd
import sys

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(dir))

from utility import data_parser

pd.set_option('display.max_rows', None)

"""
Parses data file to candlestick with orderbook

Input data a dataframe in following format:

    [0:Time, 2:Tick type, 3:Symbol, 4:Price, 5:Size, 6:Trade flag, 7~18:Order book]

Output: Dataframe with candlestick data

    ["Bar number", "Time", "Open", "High", "Low", "Close", "Size", "Bid/Ask Price/Size 1/2/3"]
"""
def candlestick(ticker, start_date, end_date, **kwargs):
    data_df= data_parser.complete_data(ticker, start_date, end_date)
    list = [[np.NAN]*19] * len(data_df)

    candlestick_df = pd.DataFrame(list, columns=["bar number", "time", "open", "high", "low", "close", "size", "bid price 1", "bid size 1", "bid price 2", "bid size 2", "bid price 3", "bid size 3", "ask price 1", "ask size 1", "ask price 2", "ask size 2", "ask price 3", "ask size 3"]) 

    market_open = "14:30:00"
    market_close = "21:00:00"

    bar_number = 0
    last_traded_price = 0.0
    open, high, low, close = np.NAN, np.NAN, np.NAN, np.NAN 
    bid, bid_size, ask, ask_size = 0.0, 0, 0.0, 0
    b2, bs2, b3, bs3, a2, as2, a3, as3 = 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0

    for row in range(len(data_df)):
        time = data_df["time"][row].split(" ")[1]
        if time < market_open or time > market_close:
            continue

        update_type = data_df["tick type"][row]

        if update_type != "T":
            bid = data_df["bid price 1"][row]
            bid_size = data_df["bid size 1"][row]
            ask = data_df["ask price 1"][row]
            ask_size = data_df["ask size 1"][row]

            if row == 0 or data_df["time"][row].split(" ")[0] > data_df["time"][row - 1].split(" ")[0]: # first update of the day is quote
                bar_number = 0     # reset bar number on a new day
                high = ask
                low = bid
                open = close = (high + low)/2

            else:
                if bar_number != candlestick_df["bar number"][len(candlestick_df)-1]:   # first quote update for a candlestick
                    high = ask
                    low = bid
                else:
                    high = ask if ask >= high else high
                    low = bid if bid <= low else low

                close = (bid + ask)/2

            candlestick_df.loc[row] = [bar_number, data_df["time"][row], open, high, low, close, 0, bid, bid_size, data_df["bid price 2"][row], data_df["bid size 2"][row], data_df["bid price 3"][row], data_df["bid size 3"][row], ask, ask_size, data_df["ask price 2"][row], data_df["ask size 2"][row], data_df["ask price 3"][row], data_df["ask size 3"][row]]
            continue

        if update_type == "T":
            close = data_df["price"][row]

            if row == 0 or data_df["time"][row].split(" ")[0] > data_df["time"][row - 1].split(" ")[0]: # first update of the day is trade (highly unlikely)
                bar_number = 0      # reset bar number on a new day
                open = high = low = close
                b2, bs2, b3, bs3, a2, as2, a3, as3 = 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0

            else:
                open = last_traded_price
                b2 = data_df["bid price 2"][row-1]
                bs2 = data_df["bid size 2"][row-1]
                b3 = data_df["bid price 3"][row-1]
                bs3 = data_df["bid size 3"][row-1]
                a2 = data_df["ask price 2"][row-1]
                as2 = data_df["ask size 2"][row-1]
                a3 = data_df["ask price 3"][row-1]
                as3 = data_df["ask size 3"][row-1]


            candlestick_df.loc[row] = [bar_number, data_df["time"][row], open, max(high, close), min(low, close), close, data_df["size"][row], bid, bid_size, b2, bs2, b3, bs3, ask, ask_size,a2, as2, a3, as3]

            if close != last_traded_price:
                bar_number += 1

            last_traded_price = close

    candlestick_df = candlestick_df[candlestick_df["bar number"] >= 0]
    candlestick_df.reset_index(drop=True, inplace=True)

    return candlestick_df

