import gzip
import os
import numpy as np
import pandas as pd
import random


# Converts string timestamp to pandas timestamp
def to_timestamp(input):
    time = input.split(" ")
    return pd.to_datetime(time[0] + 'T' + time[1] + 'Z', format='%Y-%m-%dT%H:%M:%S.%fZ')


def text_tick(ticker, start_date, end_date):
    """
    Reads trade tick csv file and save into dataframe

    :param ticker: Ticker symbol of interest
    :param start_date: start date to parse in YYYYMMDD format
    :param end_date: end date to parse in YYYYMMDD format
    :return: data frame with columns [time, message type, symbol, price, size, trade flag, bid/ask price/size 1/2/3]
    """
    trade_df = pd.DataFrame(columns=["COLLECTION_TIME", "MESSAGE_ID", "MESSAGE_TYPE", "SYMBOL", "PRICE", "SIZE", "TRADE_ID", "bid price 1", "bid size 1", "bid price 2", "bid size 2", "bid price 3", "bid size 3", "ask price 1", "ask size 1", "ask price 2", "ask size 2", "ask price 3", "ask size 3", "TRADE_FLAGS"])
    date = pd.to_datetime(start_date, format='%Y%m%d')

    while date != pd.to_datetime(end_date, format='%Y%m%d')+pd.Timedelta(days=1):
        file_path = f"../../iexdownloaderparser/data/book_snapshots/{date.year}{date.month if date.month >= 10 else '0'+str(date.month)}{date.day if date.day >= 10 else '0'+str(date.day)}_trades.csv.gz"
        
        # Parse file if path exists
        if (os.path.isfile(file_path)) and os.access(file_path, os.R_OK):
            df = pd.read_csv(file_path, compression="gzip")

            # market_open = f"{date.date()} 14:30:00"
            # market_close = f"{date.date()} 21:00:00"

            # df = df.loc[(df["COLLECTION_TIME"] > market_open) & (df["COLLECTION_TIME"] < market_close)]

            trade_df = pd.concat([trade_df, df])

        date += pd.Timedelta(days=1)

    trade_df.drop(columns=["MESSAGE_ID", "TRADE_ID"], inplace = True)
    trade_df.rename(columns={"COLLECTION_TIME": "time", "MESSAGE_TYPE": "tick type", "SYMBOL": "symbol", "PRICE": "price", "SIZE": "size", "TRADE_FLAGS": "trade flags"}, inplace=True)
    trade_df.reset_index(drop=True, inplace=True)

    return trade_df


def order_book(ticker, start_date, end_date):
    """
    Reads orderbook updaet csv file and save into dataframe

    :param ticker: Ticker symbol of interest
    :param start_date: start date to parse in YYYYMMDD format
    :param end_date: end date to parse in YYYYMMDD format
    :return: data frame with columns [time, message type, symbol, price, size, trade flag, bid/ask price/size 1/2/3]
    """
    order_book_df = pd.DataFrame(columns=["COLLECTION_TIME", "MESSAGE_ID", "MESSAGE_TYPE", "SYMBOL", "price", "size","trade flags", "BID_PRICE_1", "BID_SIZE_1", "BID_PRICE_2", "BID_SIZE_2", "BID_PRICE_3", "BID_SIZE_3", "ASK_PRICE_1", "ASK_SIZE_1", "ASK_PRICE_2", "ASK_SIZE_2", "ASK_PRICE_3", "ASK_SIZE_3"])
    date = pd.to_datetime(start_date, format='%Y%m%d')

    while date != pd.to_datetime(end_date, format='%Y%m%d')+pd.Timedelta(days=1):
        file_path = f"../../iexdownloaderparser/data/book_snapshots/{date.year}{date.month if date.month >= 10 else '0'+str(date.month)}{date.day if date.day >= 10 else '0'+str(date.day)}_book_updates.csv.gz"

        # Parse file if path exists
        if (os.path.isfile(file_path)) and os.access(file_path, os.R_OK):
            df = pd.read_csv(file_path, compression="gzip")

            # market_open = f"{date.date()} 14:30:00"
            # market_close = f"{date.date()} 21:00:00"

            # df = df.loc[(df["COLLECTION_TIME"] > market_open) & (df["COLLECTION_TIME"] < market_close)]

            order_book_df = pd.concat([order_book_df, df])

        date += pd.Timedelta(days=1)

    order_book_df.drop(columns=["MESSAGE_ID"], inplace = True)
    order_book_df.rename(columns={"COLLECTION_TIME": "time", "MESSAGE_TYPE": "tick type", "SYMBOL": "symbol", "BID_PRICE_1": "bid price 1", "BID_SIZE_1": "bid size 1", "BID_PRICE_2": "bid price 2", "BID_SIZE_2": "bid size 2", "BID_PRICE_3": "bid price 3", "BID_SIZE_3": "bid size 3", "ASK_PRICE_1": "ask price 1", "ASK_SIZE_1": "ask size 1", "ASK_PRICE_2": "ask price 2", "ASK_SIZE_2": "ask size 2", "ASK_PRICE_3": "ask price 3", "ASK_SIZE_3": "ask size 3"}, inplace=True)
    order_book_df.reset_index(drop=True, inplace=True)

    return order_book_df


def complete_data(ticker, start_date, end_date):
    """
    combines the trade and order book update dataframe, which is an input for candlestick generation

    :param ticker: Ticker symbol of interest
    :param start_date: start date to parse in YYYYMMDD format
    :param end_date: end date to parse in YYYYMMDD format
    :return: concated dataframe of trade and orderbook update
    """
    trade = text_tick(ticker, start_date, end_date)
    deep = order_book(ticker, start_date, end_date)

    df = pd.concat([trade, deep])
    df.sort_values(by=["time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

