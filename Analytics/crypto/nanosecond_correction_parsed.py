#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 04:49:16 2023

@author: akshay
"""
import dask.dataframe as dd
import glob
import os

def find_txt_files(root_dir):
    search_pattern = os.path.join(root_dir, '**', '*.txt')
    txt_files = glob.glob(search_pattern, recursive=True)
    return txt_files

def process_file(file_path):
    ddf = dd.read_csv(file_path, sep=',', header=None)
    cols = ['COLLECTION_TIME', 'SOURCE_TIME', 'SEQ_NUM', 'TICK_TYPE', 'MARKET_CENTER', 'SIDE',
            'PRICE', 'SIZE', 'NUM_ORDERS', 'IS_IMPLIED', 'REASON', 'IS_PARTIAL']
    ddf.columns = cols

    # Convert to datetime
    ddf['COLLECTION_TIME'] = dd.to_datetime(ddf['COLLECTION_TIME'])
    ddf['SOURCE_TIME'] = dd.to_datetime(ddf['SOURCE_TIME'])

    # Apply formatting
    ddf['COLLECTION_TIME'] = ddf['COLLECTION_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S') + \
                                       ddf['COLLECTION_TIME'].dt.nanosecond.astype(str).str.zfill(7)
    ddf['SOURCE_TIME'] = ddf['SOURCE_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S') + \
                                   ddf['SOURCE_TIME'].dt.nanosecond.astype(str).str.zfill(7)

    # Compute the result
    df_formatted = ddf.compute()

    # Save the file in the same path with a different name
    df_formatted.to_csv(file_path, index=False)
    print(f"Saved formatted file to {file_path}")

# Replace this with the path to your root directory
root_directory = 'parsed_files'

# Find .txt files
txt_files = find_txt_files(root_directory)

# Process each file
for file in txt_files:
    process_file(file)

