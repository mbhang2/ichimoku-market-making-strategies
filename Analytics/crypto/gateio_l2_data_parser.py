#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 20:41:12 2023

@author: akshay
"""

import gzip
import csv
import os
import re
import argparse
from datetime import datetime
import numpy as np
import pandas as pd
import multiprocessing
import shutil
"""
This script is designed to parse and process trading data from Gate.io, a cryptocurrency exchange. 
It reads compressed CSV files from a structured directory (organized by year and month), processes 
the data according to specific requirements, and outputs transformed data into a specified output directory.

Classes:
    GateIoDataParser: A class to handle the parsing of Gate.io data.

Functions:
    main(): Entry point for the script.

Class GateIoDataParser:
    Parses data files from Gate.io.

    Attributes:
        input_dir (str): Directory path where input files are located.
        output_dir (str): Directory path where output files will be saved.

    Methods:
        parse(): Orchestrates the parsing process for each year and month in the input directory.
        parse_month_folder(month_path, year, month): Parses files in a specified month folder.
        parse_file(input_path, output_dir, filename): Parses an individual file and saves the processed output.
        read_data_gateio(path, file, us_central_time=False): Reads and preprocesses data from a .csv.gz file.
        ss_format_data(df, market='Gateio', drop_set=True): Transforms data into a specific format.

Function main:
    Sets up command-line argument parsing and initiates the parsing process.

    The script accepts two command-line arguments:
        --input_path (str): Path to the input directory.
        --output_path (str): Path to the output directory.

Usage:
    Run the gateio_l2_data_parser.sh bash script from the command line with the required arguments.
    
"""

def process_negative_data(df_sorted):
    negative_rows = df_sorted[(df_sorted['cumulative_amount'] < 0) & (df_sorted['cumulative_amount'] < -1e-08)]

    # Iterate over each negative row and adjust
    for idx, negative_row in negative_rows.iterrows():
        side = negative_row['side']
        price = negative_row['price']
        cum_amount = abs(negative_row['cumulative_amount'])
        timestamp = negative_row['timestamp']
        action = 'take'
        begin_id = negative_row['begin_id']
        merged = 1
        tmp = pd.DataFrame(columns=df_sorted.columns)
        filled_df = pd.DataFrame(columns=df_sorted.columns)
        dtype_mapping = df_sorted.dtypes.apply(lambda x: x.name).to_dict()
        filled_df = filled_df.astype(dtype_mapping)
        tmp = filled_df.astype(dtype_mapping)
        # Find rows to adjust based on 'side'
        if side == 2:  # Assuming '1' is sell
            adjust_rows = df_sorted[(df_sorted['side'] == side) & (df_sorted['price'] >= price) & (df_sorted['begin_id'] < negative_row['begin_id'])]
            prices_no_zero = adjust_rows.groupby(['price'])['amount'].sum().reset_index()
            prices_no_zero = prices_no_zero.loc[prices_no_zero.amount > 0, 'price']
            adjust_rows = adjust_rows[adjust_rows.action == 'make']
            adjust_rows = adjust_rows[adjust_rows['price'].isin(prices_no_zero)]
            adjust_rows = adjust_rows.sort_values(['price', 'begin_id'], ascending=[True, False])
            # adjust_rows = adjust_rows[adjust_rows.action == 'make']
        else:  # Assuming '2' or other is buy
            adjust_rows = df_sorted[(df_sorted['side'] == side) & (df_sorted['price'] <= price) & (df_sorted['begin_id'] < negative_row['begin_id'])]
            prices_no_zero = adjust_rows.groupby(['price'])['amount'].sum().reset_index()
            prices_no_zero = prices_no_zero.loc[prices_no_zero.amount > 0, 'price']
            adjust_rows = adjust_rows[adjust_rows.action == 'make']
            adjust_rows = adjust_rows[adjust_rows['price'].isin(prices_no_zero)]
            adjust_rows = adjust_rows.sort_values(['price', 'begin_id'], ascending=[False, False])
        
        if adjust_rows.empty:
            continue
        else:
            adjust_rows.reset_index(drop = True, inplace = True)
            adjust_rows['roll_sum'] = adjust_rows.amount.cumsum()
            # Recalculate cumulative sum for the adjusted rows
            first_index = (adjust_rows['roll_sum'] > cum_amount).idxmax()
            
            for ids in range(first_index):
                match_price = adjust_rows.loc[ids, 'price']
                amount = adjust_rows.loc[ids, 'amount']
                match_begin_id = begin_id + np.round(np.random.uniform(0,1),1)*(ids + 1)
                match_cum = max(adjust_rows.loc[ids, 'cumulative_amount'] - cum_amount,0)
                row_entries = [timestamp, side, action, match_price, amount, match_begin_id, merged, match_cum]
                
                filled_df.loc[len(filled_df)] = row_entries
            if not filled_df.empty:
                tmp = pd.concat([tmp, filled_df], ignore_index=True)
            
    idx_remove = [idx for idx, negative_row in negative_rows.iterrows()]
    df_sorted = df_sorted.drop(idx_remove)
    df_sorted.reset_index(drop=True, inplace = True)
    if not tmp.empty:
        df_sorted = pd.concat([df_sorted, tmp], ignore_index= True)
    return df_sorted

def process_data(args):
    df, first_file = args
    # df.loc[df['action'] == 'set', 'action'] = 'make'
    # df.loc[df['timestamp'].dt.time.between(time_start, time_end), 'action'] = 'make'
    # df = df[df['action'] != 'set']
    df = df[df['amount'] >= 0]
    set_begin_id = df.loc[df.action == 'set','begin_id'].unique()
    set_begin_id = set_begin_id[0] if len(set_begin_id) else None

    df.loc[df['action'] == 'set', 'action'] = 'make'
    df['amount'] = np.round(df['amount'])
    df['price'] = np.round(df['price'],2)
    df['amount'] = np.where(df['action'] == 'take', df['amount'] * -1, df['amount'])
    df_sorted = df.sort_values(by=['begin_id'])
    
    df_sorted['cumulative_amount'] = df_sorted.groupby(['side', 'price'])['amount'].cumsum()
    df_sorted = df_sorted[(df_sorted['cumulative_amount'] > 1e-08) | (df_sorted['cumulative_amount'] < -1e-08)]    
    pos_check = df_sorted[(df_sorted['cumulative_amount'] < -1e-08)].shape[0]
    df_sorted.reset_index(drop=True, inplace = True)
    i = 0
    while pos_check != 0 and i !=5: 
        df_sorted = process_negative_data(df_sorted)
        df_sorted['cumulative_amount'] = df_sorted.groupby(['side', 'price'])['amount'].cumsum()
        df_sorted = df_sorted[(df_sorted['cumulative_amount'] > 1e-08) | (df_sorted['cumulative_amount'] < -1e-08)]    
        df_sorted = df_sorted.sort_values(by=['begin_id'])
        df_sorted.reset_index(drop=True, inplace = True)
        i += 1
        pos_check = df_sorted[(df_sorted['cumulative_amount'] < -1e-08)].shape[0]
    
    if pos_check != 0:
        df_sorted = df_sorted[df_sorted['amount'] >= 0]
    if not first_file:
        if set_begin_id != None:
            df_sorted = df_sorted[df_sorted['begin_id'] != set_begin_id]
    
    df_sorted.reset_index(drop=True, inplace = True)
    df_sorted['timestamp'] = pd.to_datetime(df_sorted['timestamp'])
    df_sorted.begin_id = df_sorted.begin_id*100
    df_sorted = df_sorted.sort_values(by=['timestamp'])
    return df_sorted

class GateIoDataParser:
    def __init__(self, input_dir, output_dir, symbol = 'BTC_USDT', parallel = False):
        self.input_dir = input_dir
        self.output_dir = os.path.join(output_dir, symbol)
        self.symbol = symbol
        self.parallel = parallel
    
    @staticmethod
    def extract_date(filename):
        # Use regex to extract the date part from the filename
        match = re.search(r'(\d{4}\d{2}\d{2})\.csv\.gz$', filename)
        return int(match.group(1)) if match else None
    
    @staticmethod
    def list_csv_gz_files(directory):
        csv_gz_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".csv.gz"):
                    file_path = os.path.join(root, file)
                    csv_gz_files.append(file_path)
        csv_gz_files.sort(key=lambda x: int(os.path.basename(x).split('.')[0].split('-')[-1]))
        return csv_gz_files                     
    
    def parse(self):
        for year_dir in os.listdir(self.input_dir):
            year_path = os.path.join(self.input_dir, year_dir)
            if os.path.isdir(year_path):
                for month_dir in os.listdir(year_path):
                    month_path = os.path.join(year_path, month_dir)
                    if os.path.isdir(month_path):
                        if self.parallel:
                            self.parse_month_folder_parallel(month_path, year_dir, month_dir)
                        else:
                            self.parse_month_folder(month_path, year_dir, month_dir)
    
    def parse_month_folder(self, month_path, year, month):
        output_month_dir = os.path.join(self.output_dir, year, month)
        if not os.path.exists(output_month_dir):
            os.makedirs(output_month_dir)
        
        files = [f for f in os.listdir(month_path) if f.endswith('.csv.gz')]
        # Sort files based on the extracted date
        files = sorted(files, key=GateIoDataParser.extract_date)
        for file in files:
            if file.endswith(".csv.gz"):
                self.parse_file(os.path.join(month_path, file), output_month_dir, file)
                
    def parse_month_folder_parallel(self, month_path, year, month):
        output_month_dir = os.path.join(self.output_dir, year, month)
        if not os.path.exists(output_month_dir):
            os.makedirs(output_month_dir)
            
        files = [f for f in os.listdir(month_path) if f.endswith('.csv.gz')]
        # Sort files based on the extracted date
        files = sorted(files, key=GateIoDataParser.extract_date)
        all_files = GateIoDataParser.list_csv_gz_files(self.input_dir)
        first_file = all_files[0].rsplit('/')[-1]
        
        # Determine the number of worker processes
        batch_size = 2
        
        if files[0] == first_file:
            self.parse_file(os.path.join(month_path, files[0]), output_month_dir, files[0])
            remaining_files = files[1:]

            # Process the remaining files in parallel
            if remaining_files:
                for i in range(0, len(remaining_files), batch_size):
                    batch = remaining_files[i:i + batch_size]
                    with multiprocessing.Pool(batch_size) as pool:
                        pool.starmap(self.parse_file, [(os.path.join(month_path, f), output_month_dir, f) for f in remaining_files])
        

    def parse_file(self, input_path, output_dir, filename):
        date = filename.split('-',1)[-1].split('.')[0]
        all_files = GateIoDataParser.list_csv_gz_files(self.input_dir)
        first_file = all_files[0].rsplit('/')[-1]
        
        sym_name = f'tick_MSFT_{date}.txt'
        output_path = os.path.join(output_dir, sym_name)
        print("----------------------------------------------")
        print(f"Starting data parsing of {self.symbol} for {date}")
        print("----------------------------------------------")
        
        if filename == first_file:
            flags = [True] + [False]*23
        else:
            flags = [False]*24
            
        month_path = input_path.rsplit('/', 1)[0]
        df = self.read_data_gateio(month_path, filename)
        combined_df = self.ss_format_data(df, market = 'IEX', flags = flags)
        
        # Write the DataFrame to a comma-separated .txt file
        combined_df.to_csv(output_path, sep=',', index=False, header=False)
        
        sym_name_tmp = f'tick_MSFT_{date}_tmp.txt'
        temp_file_path = os.path.join(output_dir, sym_name_tmp)
        
        # Process the file
        with open(output_path, 'r') as file, open(temp_file_path, 'w') as temp_file:
            for line in file:
                # Replace ',T,IEX,,' with ',T,IEX,'
                if ',T,IEX,,' in line:
                    line = line.replace(',T,IEX,,', ',T,IEX,')
        
                # Split the line at ',T,IEX,' to isolate the part that needs further processing
                parts = line.split(',T,IEX,')
                if len(parts) > 1:
                    # Process the second part of the line
                    # Strip trailing commas and reconstruct the line
                    line = parts[0] + ',T,IEX,' + parts[1].rstrip(',\n') + '\n'
        
                temp_file.write(line)

        print("----------------------------------------------------------")
        print(f"Writen the parsed data of {self.symbol} for {date} in a txt file")
        print("----------------------------------------------------------")
        
        # Replace the original file with the modified temporary file
        shutil.move(temp_file_path, output_path)
    
    def read_data_gateio(self, path, file, us_central_time = False):
        df = pd.read_csv(os.path.join(path, file), compression='gzip', on_bad_lines='warn')

        df.columns = ['timestamp', 'side', 'action', 'price', 'amount', 'begin_id', 'merged']
        df.timestamp = df.timestamp.apply(datetime.utcfromtimestamp)
        if us_central_time == True:
            df.timestamp = df.timestamp.dt.tz_localize('UTC').dt.tz_convert('US/Central')
        return df
    
    def ss_format_data(self, df, market = 'IEX', flags = [False]*24):
        columns_ss = ['COLLECTION_TIME','SOURCE_TIME','SEQ_NUM','TICK_TYPE','MARKET_CENTER', 'SIDE',\
                    'PRICE','SIZE', 'NUM_ORDERS', 'IS_IMPLIED','REASON', 'IS_PARTIAL']
        
        columns_ss_trade = ['COLLECTION_TIME','SOURCE_TIME','SEQ_NUM','TICK_TYPE','MARKET_CENTER',\
                    'PRICE','SIZE']
        # Create a dictionary to hold each hour's DataFrame
        hourly_dfs = []
        grouped = df.groupby(df['timestamp'].dt.hour)
        for hour, group in grouped:
            hourly_dfs.append(group)
        args = zip(hourly_dfs, flags)
        num_procs = int(multiprocessing.cpu_count() - 4)

        with multiprocessing.Pool(processes=num_procs) as pool:
            results = pool.map(process_data, args)

        df_sorted = pd.concat(results, ignore_index=True)
        df_sorted = df_sorted.sort_values(by=['begin_id']).reset_index(drop=True)
        ss_df_trade = pd.DataFrame(columns = columns_ss_trade)
        df_trade = df_sorted[df_sorted.action == 'take']
        ss_df_trade['COLLECTION_TIME'] = df_trade['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S') + \
                                       df_trade['timestamp'].dt.nanosecond.astype(str).str.zfill(7)
        ss_df_trade['SOURCE_TIME'] = df_sorted['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S') + \
                                   df_sorted['timestamp'].dt.nanosecond.astype(str).str.zfill(7)
        
        ss_df_trade['SEQ_NUM'] = df_trade['begin_id'].copy() - 1
        ss_df_trade['SEQ_NUM'] = np.round(ss_df_trade['SEQ_NUM']).astype(int)
        ss_df_trade['TICK_TYPE'] = 'T'
        ss_df_trade['MARKET_CENTER'] = market
        ss_df_trade['PRICE'] = np.round(df_trade['price'].copy(),2)
        ss_df_trade['PRICE'] = ss_df_trade['PRICE'].map(lambda x: '{:.6f}'.format(x))
        ss_df_trade['SIZE'] = df_trade['amount'].copy().abs()
        ss_df_trade['SIZE'] = np.round(ss_df_trade['SIZE']).astype(int)
       
        ss_df = pd.DataFrame(columns = columns_ss)   
        ss_df['COLLECTION_TIME'] = df_sorted['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S') + \
                                       df_sorted['timestamp'].dt.nanosecond.astype(str).str.zfill(7)
        ss_df['SOURCE_TIME'] = df_sorted['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S') + \
                                   df_sorted['timestamp'].dt.nanosecond.astype(str).str.zfill(7)
        ss_df['SEQ_NUM'] = df_sorted['begin_id'].copy()
        ss_df['SEQ_NUM'] = np.round(ss_df['SEQ_NUM']).astype(int)
        ss_df['TICK_TYPE'] = 'P'
        ss_df['MARKET_CENTER'] = market
        side_mapping = {'buy': 1, 2: 1, 'sell': 2, 1: 2}
        ss_df['SIDE'] = df_sorted['side'].replace(side_mapping).astype(int)
        ss_df['PRICE'] = np.round(df_sorted['price'].copy(),2)
        ss_df['PRICE'] = ss_df['PRICE'].map(lambda x: '{:.6f}'.format(x))
        ss_df['SIZE'] = df_sorted['cumulative_amount'].copy()
        ss_df['SIZE'] = np.round(ss_df['SIZE']).astype(int)
        
        # Concatenate the DataFrames
        combined_df = pd.concat([ss_df, ss_df_trade], ignore_index=True)
        combined_df['SIDE'] = combined_df['SIDE'].fillna(0)
        combined_df['SIDE'] = combined_df['SIDE'].astype(int)
        combined_df['SIDE'] = combined_df['SIDE'].replace(0,'')
        # Sort by SEQ_NUM column
        combined_df = combined_df.sort_values(by=['COLLECTION_TIME','SEQ_NUM'])
        
        return combined_df

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Parse Gate.io Data')
    parser.add_argument('--input_path', type=str, required=True, help='Path to the input directory')
    parser.add_argument('--output_path', type=str, required=True, help='Path to the output directory')
    parser.add_argument('--symbol', type=str, required=False, help='Name of the pair being traded (e.g. BTC_USDT)')
    parser.add_argument('--parallel', type=str, required=False, help='Whether to run scripts parallely or sequentially')
    # Parse arguments
    args = parser.parse_args()

    # Create an instance of the parser with command line arguments
    input_directory = args.input_path
    output_directory = args.output_path
    symbol = args.symbol
    parallel = args.parallel
    parse_obj = GateIoDataParser(input_directory, output_directory, symbol, parallel)

    # Run the parser
    parse_obj.parse()

if __name__ == '__main__':
    main()

# parser = GateIoDataParser("downloaded_files", "parsed_files")
# parser.parse()

