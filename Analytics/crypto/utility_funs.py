# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 16:14:16 2023

@author: apand
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime
import multiprocessing

def find_dir(dir_name, start = '.'):
    '''
    Parameters
    ----------
    start : String
        DESCRIPTION. The repository from where you want the for the 
        folder/file to start from. The default is the '.' which is the 
        current working directory.
    dir_name : String
        DESCRIPTION. The name of the directory you are searching for

    Returns
    -------
    Path of the directory where the dirname exists.

    '''
    for dirpath, dirnames, _ in os.walk(start):
        for dirname in dirnames:
            if dirname == dir_name:
                global rep
                rep = dirpath
                return rep
            else:
                continue

def read_data_gateio(path,file, us_central_time = False):
    '''
    
    Parameters
    ----------
    path : String
        The path of the directory where the file resides.
    file : String
        The name of the file.

    Returns
    -------
    df : Pandas DataFrame
        Formatted Dataframe which has the data for a given crypto currency with fields:
            'timestamp', 'side', 'action', 'price', 'amount', 'begin_id', 'merged'. 
    '''

    df = pd.read_csv(os.path.join(path, file), compression='gzip')
    df.columns = ['timestamp', 'side', 'action', 'price', 'amount', 'begin_id', 'merged']
    df.timestamp = df.timestamp.apply(datetime.utcfromtimestamp)
    if us_central_time == True:
        df.timestamp = df.timestamp.dt.tz_localize('UTC').dt.tz_convert('US/Central')
    return df

def calculate_vwap(df, window = '1T'):
    '''

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe which has the data for a given crypto currency with fields:
            'timestamp', 'side', 'action', 'price', 'amount', 'begin_id', 'merged'.
    
    window : string, optional
        DESCRIPTION. The default is '1T'.

    Returns
    -------
    df : Formatted Dataframe with volume weighted average price.

    '''
    #Break the data into buy and sell dataframes
    buy_df = df[df.side == 'buy']
    sell_df = df[df.side == 'sell']
    
    def vwap(df):
        # Filter DataFrame for 'set' and 'make' actions    
        filtered_df = df[df['action'].isin(['set', 'make'])].sort_values('timestamp')
        filtered_df = filtered_df.groupby(['timestamp', 'price'])['amount'].sum().reset_index()
        # Calculate VWAP
        # Multiply price by amount to get the total traded price for each row
        filtered_df['price_x_amount'] = filtered_df['price'] * filtered_df['amount']
        
        # Use a rolling window of 1 minute to calculate sum of price_x_amount and sum of amount
        filtered_df.set_index('timestamp', inplace=True)
        rolling_sum = filtered_df[['price_x_amount', 'amount']].rolling(window).sum()
        filtered_df['vwap'] = rolling_sum['price_x_amount'] / rolling_sum['amount']
        
        # Reset index
        filtered_df.reset_index(inplace=True)
        
        # Forward fill the VWAP values for 'take' actions in the original DataFrame
        df = df.sort_values('timestamp')
        df[f'vwap_{window}'] = filtered_df['vwap']
        df[f'vwap_{window}'].fillna(method='ffill', inplace=True)
        
        return df

    buy_df = vwap(buy_df)
    sell_df = vwap(sell_df)
    
    #Concatinate back to one dataframe
    df = pd.concat([buy_df,sell_df]).sort_values('timestamp')
    
    return df

def active_trade_range(df, range_freq = 2500):
    '''

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe which has the data for a given crypto currency with fields:
            'timestamp', 'side', 'action', 'price', 'amount', 'begin_id', 'merged'.

    range_freq : integer, optional
        Price range window in which you would like to break down the search. 
        The default is 2500.

    Returns
    -------
    df : Formatted dataframe within the active trading price range.


    '''
    # Define price buckets - this can be customized
    df_take = df[df['action'] == 'take']
    bucket_intervals = pd.interval_range(start=df_take['price'].min(), end=df_take['price'].max(), freq=range_freq)
    # The freq parameter in interval_range sets the width of each bucket. Adjust it as needed.

    # Assign each price to a bucket
    df_take['price_bucket'] = pd.cut(df_take['price'], bins=bucket_intervals)

    # Group by price_bucket and count the number of 'take' actions
    price_distribution = df_take.groupby('price_bucket').size().reset_index(name='count')
    
    # Find the price bucket with the maximum count
    max_count_bucket = price_distribution.loc[price_distribution['count'].idxmax(), 'price_bucket']

    # Filter the main DataFrame for rows within this price range
    df = df[(df['price'] >= max_count_bucket.left) & (df['price'] <= max_count_bucket.right)]
    
    return df
    
# Function to calculate OFI
def calculate_ofi(df):
    '''
    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe which has the data for a given crypto currency with fields:
            'timestamp', 'side', 'action', 'price', 'amount', 'begin_id', 'merged'.

    Returns
    -------
    df : Pandas Dataframe
        Dataframe which has the data for a given crypto currency with fields:
            'timestamp', 'side', 'action', 'price', 'amount', 'begin_id', 'merged'.

    '''
    
    # Create a mask for rows where action is 'take'
    take_action_mask = df['action'] == 'take'
    # Calculate OFI
    df['ofi'] = np.where(take_action_mask & (df['side'] == 'buy'), df['amount'], 
                         np.where(take_action_mask & (df['side'] == 'sell'), -df['amount'], 0))
    return df

def ss_format_data(df, market = 'Gateio', drop_set = True):
    columns_ss = ['COLLECTION_TIME','SOURCE_TIME','SEQ_NUM','TICK_TYPE','MARKET_CENTER', 'SIDE',\
                  'PRICE','SIZE']
    if drop_set:
        df.loc[df.action == 'set', 'action'] = 'make'
    df_sorted = df.sort_values(by=['timestamp', 'begin_id'])
    df_sorted = df_sorted[df_sorted['amount'] >= 0]
    min_amount = df_sorted.amount.min()
    df_sorted['amount'] = np.where(df_sorted['action'] == 'take', df_sorted['amount'] * -1, df_sorted['amount'])
    df_sorted['cumulative_amount'] = df_sorted.groupby(['side', 'price'])['amount'].cumsum()
    ss_df = pd.DataFrame(index= df_sorted.index,columns = columns_ss)   
    ss_df['COLLECTION_TIME'] = df_sorted['timestamp'].copy()
    ss_df['SOURCE_TIME'] = df_sorted['timestamp'].copy()
    ss_df['TICK_TYPE'] = 'D'
    ss_df['MARKET_CENTER'] = market
    side_mapping = {'buy': 1, 2: 1, 'sell': 2, 1: 2}
    ss_df['SIDE'] = df_sorted['side'].replace(side_mapping)
    ss_df['SEQ_NUM'] = df_sorted['begin_id'].copy()
    ss_df['PRICE'] = df_sorted['price'].copy()
    ss_df['SIZE'] = df_sorted['cumulative_amount'].copy()
    # df_sorted['cumulative_amount'] = np.where((df_sorted.cumulative_amount < 0) & \
    # (df_sorted.cumulative_amount > -1e-08), 0, df_sorted['cumulative_amount'] )
    # df_sorted_pos = df_sorted[df_sorted.cumulative_amount>= 0]
    # df_sorted_neg = df_sorted[df_sorted.cumulative_amount < 0]
