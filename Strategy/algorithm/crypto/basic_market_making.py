#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 02:15:36 2023

@author: akshay
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
import os
import pytz
import time
import multiprocessing
import matplotlib.pyplot as plt
import mplfinance as mpf

from utility_funs import *

start = '/media'

base_dir = "downloaded_files_gateio"
rep = find_dir(base_dir, start)

path = os.path.join(rep, base_dir)
files = [f for f in os.listdir(path) if f.endswith('.gz')]

for i in range(len(files)):
    df = read_data_gateio(path, files[i])
    df['side'] = df['side'].map({1: 'sell', 2: 'buy'})
    df = df[df['amount'] >= 0]
    # Create a mask where action is 'set'
    is_set_action = df['action'] == 'set'

    # Forward fill the 'amount' where action is 'set', else use NaN
    df['base'] = df['amount'].where(is_set_action).ffill()

    # Handling prices not encountered before (if any)
    df['base'] = df['base'].fillna(0)
    
    # Find the active price range
    df = active_trade_range(df)
    
    #Find the volume-weighted average price
    df = calculate_vwap(df) # Default is 1-minute vwap
    df = calculate_vwap(df, window = '1S') # Calculating 1-second vwap
    
    # df = calculate_ofi(df)
   
    # Sort DataFrame by 'timestamp' and 'side'

# Define parameters for strategy
spread_threshold = 0.02  # Example threshold for bid-ask spread percentage
imbalance_threshold = 10  # Example threshold for order imbalance

# Assuming 'price' column represents the latest matched price
def calculate_spread(df):
    # Calculate bid-ask spread
    ask_price = df[df['side'] == 1]['price'].min()  # Lowest sell price
    bid_price = df[df['side'] == 2]['price'].max()  # Highest buy price
    spread = ask_price - bid_price
    spread_percentage = spread / ask_price
    return spread_percentage

def calculate_order_imbalance(df):
    # Calculate order imbalance
    buy_volume = df[df['side'] == 2]['amount'].sum()
    sell_volume = df[df['side'] == 1]['amount'].sum()
    imbalance = buy_volume - sell_volume
    return imbalance

# Strategy execution
spread_percentage = calculate_spread(df)
imbalance = calculate_order_imbalance(df)

if spread_percentage < spread_threshold and imbalance > imbalance_threshold:
    print("Place Buy Order")
elif spread_percentage < spread_threshold and imbalance < -imbalance_threshold:
    print("Place Sell Order")
else:
    print("No Action")

# Add your order placement logic in place of print statements
