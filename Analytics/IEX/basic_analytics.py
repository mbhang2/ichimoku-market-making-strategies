import numpy as np
import file_parser
import os
import pandas as pd



# Read all symbols from the all_tickers file
with open('all_tickers', 'r') as f:
    all_symbols = [line.strip() for line in f.read().splitlines()]


# Dictionary to store dataframes for each ticker
df_dict = {}

# Path to the Sample_Data directory
base_dir = "Sample_Data"

for symbol in all_symbols:
    # Get all .txt files for the current symbol
    files = [f for f in os.listdir(os.path.join(base_dir, symbol)) if f.endswith('.txt')]
    
    # Sort files based on the timestamp
    files_sorted = sorted(files, key=lambda x: x.split('_')[-1])

    # print(files_sorted)
    # break
    
    # Read and concatenate dataframes
    df_list = [pd.read_csv(os.path.join(base_dir, symbol, f)) for f in files_sorted]

    # ge number of columns in each dataframe
    num_columns = df_list[0].shape[1]

    # add column names to each dataframe [Column_0, Column_1, Column_2, ...]
    for i in range(len(df_list)):
        df_list[i].columns = ['Column_' + str(j) for j in range(num_columns)]

    # add an index column to each dataframe


    # print shape of each dataframe
    # df_concatenated = pd.concat(df_list, ignore_index=True)
    # concantenate all rows
    df_concatenated = pd.concat(df_list, axis=0, ignore_index=False)

    # print(df_concatenated.iloc[:, 5].head())
    
    # Store the concatenated dataframe in the dictionary
    df_dict[symbol] = df_concatenated

    # if symbol == "AAPL":
        # print dimensions

# # Helper function to retrieve the dataframe for a given symbol
def get_dataframe(symbol):
    return df_dict.get(symbol, None)

# # Example Usage
df_apple = get_dataframe('AAPL')
print(df_apple.head())

