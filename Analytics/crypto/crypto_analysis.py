# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 19:10:14 2023

@author: apand
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
import os
import pytz
import matplotlib.pyplot as plt
import mplfinance as mpf

from utility_funs import *

start = '/media'

base_dir = "downloaded_files_gateio"
rep = find_dir(base_dir, start)

def plot_bid_ask_spread(base_dir, rep, file_index = None):

    '''
    Parameters
    ----------
    base_dir : String
        DESCRIPTION. The base directory where the files exist
    rep : String
        DESCRIPTION. Path of the directory where the base directory exists.
    
    file_index [Optional] : Integer
        DESCRIPTION. Index to pick a file for analysis. The default is None.
    
    Returns
    -------
    None. Shows the plot for bid-ask spread for best bids and asks

    '''
    
    path = os.path.join(rep, base_dir)
    files = [f for f in os.listdir(path) if f.endswith('.gz')]
    # df_combined = pd.DataFrame(columns = ['timestamp', 'side', 'action', 'price', 'amount', 'begin_id', 'merged'])

    if file_index != None:    
        file = files[file_index]    
    else:
        file = files[np.random.randint(0,len(files))]

    crypto = file.split('_')[0]
    df = read_data_gateio(path, file)

    tmp_df = df.copy()
    tmp_df_set = tmp_df[tmp_df.action == 'set']
    tmp_df_take = tmp_df[tmp_df.action == 'take']

    merged_df = tmp_df[tmp_df.merged > 0]
    tmp_df_set = tmp_df_set[(tmp_df_set.price.isin(tmp_df_take.price.unique()))]
    merged_df = pd.concat([merged_df, tmp_df_set],axis = 0).reset_index(drop = True)

    # Calculate the 10th and 90th percentiles
    lower_percentile = np.percentile(merged_df['price'], 5)
    upper_percentile = np.percentile(merged_df['price'], 95)

    merged_df = merged_df[(merged_df['price'] > lower_percentile) & \
                            (merged_df['price'] < upper_percentile)]

    bid_ask_df = merged_df.loc[merged_df.action != 'make',['timestamp', 'side', 'price']]
    bid_ask_df = bid_ask_df.set_index('timestamp')
    ohlc = bid_ask_df['price'].resample('1T').ohlc()

    # Separate data for each group and resample
    ohlc1 = bid_ask_df[bid_ask_df['side'] == 1]['price'].resample('1T').ohlc()
    ohlc2 = bid_ask_df[bid_ask_df['side'] == 2]['price'].resample('1T').ohlc()

    # plt.figure(figsize=(10, 6))

    # Plot each group
    plt.plot(ohlc1.index, ohlc1.low, 'r+-', linewidth = 2, label = "Best Ask")
    plt.plot(ohlc2.index, ohlc2.high, 'go--', linewidth = 2, label = "Best Bid")

    # Adding titles and labels
    plt.title(f'Bid ask spread overtime for {crypto}', fontdict= {'fontsize': 24, 'fontweight': 'bold'})
    plt.xlabel('Timestamp', labelpad= 10, fontdict= {'fontsize': 16, 'fontweight': 'bold'})
    plt.ylabel('Price', labelpad= 10, fontdict= {'fontsize': 16, 'fontweight': 'bold'})
    plt.legend()

    # # Show plot
    plt.show()

def plot_depth_chart(base_dir, rep, file_index = None):
    '''
    Parameters
    ----------
    base_dir : String
        DESCRIPTION. The base directory where the files exist
    rep : String
        DESCRIPTION. Path of the directory where the base directory exists.
    
    file_index [Optional] : Integer
        DESCRIPTION. Index to pick a file for analysis. The default is None.
    
    Returns
    -------
    None. Shows the plot for chart depth
    
    '''
    path = os.path.join(rep, base_dir)
    files = [f for f in os.listdir(path) if f.endswith('.gz')]
    # Convert 'side' to a more readable format
    if file_index != None:    
        file = files[file_index]    
    else:
        file = files[np.random.randint(0,len(files))]
    
    crypto = file.split('_')[0]
    df = read_data_gateio(path, file)
    
    df['side'] = df['side'].map({1: 'sell', 2: 'buy'})

    # Group by price and side, and sum the amounts
    grouped = df.groupby(['price', 'side'])['amount'].sum().reset_index()
    
    # Calculate the 10th and 90th percentiles
    lower_percentile = np.percentile(grouped['price'], 5)
    upper_percentile = np.percentile(grouped['price'], 95)

    grouped = grouped[(grouped['price'] > lower_percentile) & \
                            (grouped['price'] < upper_percentile)]
    # Separate buy and sell orders
    buy_orders = grouped[grouped['side'] == 'buy']
    sell_orders = grouped[grouped['side'] == 'sell']
    
    # Sort the buy and sell dataframes
    buy_orders = buy_orders.sort_values(by='price', ascending=False)
    sell_orders = sell_orders.sort_values(by='price')
    
    # Calculate cumulative sum for buy and sell orders
    buy_orders['cumulative_amount'] = buy_orders['amount'].cumsum()
    sell_orders['cumulative_amount'] = sell_orders['amount'].cumsum()
    
    # Plotting the depth chart
    plt.figure(figsize=(10, 6))
    plt.plot(buy_orders['price'], buy_orders['cumulative_amount'], label='Buy Orders', color='green')
    plt.plot(sell_orders['price'], sell_orders['cumulative_amount'], label='Sell Orders', color='red')
    plt.title(f'Depth Chart for {crypto}', fontdict= {'fontsize': 24, 'fontweight': 'bold'})
    plt.xlabel('Price',  labelpad= 10, fontdict= {'fontsize': 16, 'fontweight': 'bold'})
    plt.ylabel('Cumulative Amount',  labelpad= 10, fontdict= {'fontsize': 16, 'fontweight': 'bold'})
    plt.legend()
    plt.show()

def plot_orderflow_imbalance(base_dir, rep, interval = '1T', day_pick = 1):
    '''
        Parameters
        ----------
        base_dir : String
            DESCRIPTION. The base directory where the files exist
        rep : String
            DESCRIPTION. Path of the directory where the base directory exists.
        
        day_pick [Optional] : Integer
            DESCRIPTION. Pick a day of the month for analysis. The default is 1.
        
        Returns
        -------
        None. Shows the plot for order flow imbalance

    '''    
    # Order flow imbalances seem to appear postive in certain periods of the day
    path = os.path.join(rep, base_dir)
    files = sorted([f for f in os.listdir(path) if f.endswith('.gz')], key = \
                   lambda x: x.split('.')[0].split('-')[-1])
    day = [datetime.strptime(f.split('.')[0].split('-')[-1][:-2], '%Y%m%d').day for f in files]
    
    ofi_resampled = pd.Series(name='ofi')
    for i in range(day.index(day_pick), len(files)):
        df = read_data_gateio(path, files[i])
        df['side'] = df['side'].map({1: 'sell', 2: 'buy'})
        
        # Apply the function to calculate Orderflow imbalance
        df = calculate_ofi(df)
       
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)

        # Resample to 10-second intervals and sum the OFI
        ofi_resampled = pd.concat([ofi_resampled,df['ofi'].resample(interval).sum()])
        if i == (len(files) - 1) or day[i] != day[i+1]:
            break
    
    crypto = files[0].split('_')[0]
    date = ofi_resampled.index.date[-1]
    # Plotting
    plt.figure(figsize=(10, 6))
    ofi_resampled.plot()
    plt.axhline(y=0, color='red', linestyle='-', linewidth=1)  
    plt.title(f'Order Flow Imbalance Over Time for {crypto} on {date}', fontdict= {'fontsize': 24, 'fontweight': 'bold'})
    plt.xlabel('Timestamp',  labelpad= 10, fontdict= {'fontsize': 16, 'fontweight': 'bold'})
    plt.ylabel('Order Flow Imbalance',  labelpad= 10, fontdict= {'fontsize': 16, 'fontweight': 'bold'})
    plt.show()