import numpy as np
import pandas as pd

import file_parser


def time_based_change(ticker, start_date, end_date, **kwargs):
    buy_frequency = {}
    sell_frequency = {}
    data = file_parser.read_date_range_tick_file(ticker, start_date, end_date)

    if data == None:
        return

    precision = kwargs.get("precision", 6)  # number of digits of sub-seconds to show

    for dataframe in data.values():
        for i in range(len(dataframe)):
            if i == 0: continue

            if dataframe["Price"][i] > dataframe["Price"][i-1]:
                t = dataframe["Collection time"][i].as_unit('s')
                decimal = round((dataframe["Collection time"][i] - t)/pd.Timedelta(seconds=1), precision)
                timestamp = (t + pd.Timedelta(seconds=decimal)).time()

                if timestamp not in buy_frequency.keys():
                    buy_frequency[timestamp] = 1
                else:
                    buy_frequency[timestamp] += 1

            if dataframe["Price"][i] < dataframe["Price"][i-1]:
                t = dataframe["Collection time"][i].as_unit('s')
                decimal = round((dataframe["Collection time"][i] - t)/pd.Timedelta(seconds=1), precision)
                timestamp = (t + pd.Timedelta(seconds=decimal)).time()

                if timestamp not in sell_frequency.keys():
                    sell_frequency[timestamp] = 1
                else:
                    sell_frequency[timestamp] += 1

    return (buy_frequency, sell_frequency)

