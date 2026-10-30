import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import pytz
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import os


scaler_price = MinMaxScaler(feature_range=(0, 1))
scaler_volume = MinMaxScaler(feature_range=(0, 1))

def make_plot(df, column_names, title, return_fig=False):

    # check if 'time_of_day_cst' column exists
    if 'time_of_day_cst' not in df.columns:
        # Convert Unix timestamp to datetime in UTC
        df['datetime_utc'] = pd.to_datetime(df['participant_timestamp'], unit='ns')

        # Convert UTC to Chicago time (CST)
        chicago_tz = pytz.timezone('America/Chicago')
        df['time_of_day_cst'] = df['datetime_utc'].dt.tz_localize('UTC').dt.tz_convert(chicago_tz).dt.strftime('%H:%M:%S')

    # Initialize an empty figure
    fig = go.Figure()

    # Iterate over each column and add a line plot for each
    for column_name in column_names:
        fig.add_trace(go.Scatter(x=df['time_of_day_cst'], y=df[column_name], mode='lines', name=column_name))

    # Update layout
    fig.update_layout(title=title, xaxis_title='Time of Day (CST)', yaxis_title='Values')

    if return_fig:
        return fig
    else:
        fig.show()


def make_plot_by_exchanges(df, exchanges):
    # Convert Unix timestamp to datetime in UTC
    df['datetime_utc'] = pd.to_datetime(df['participant_timestamp'], unit='ns')

    # Convert UTC to Chicago time (CST)
    chicago_tz = pytz.timezone('America/Chicago')
    df['time_of_day_cst'] = df['datetime_utc'].dt.tz_localize('UTC').dt.tz_convert(chicago_tz).dt.strftime('%H:%M:%S')

    # Initialize an empty figure
    fig = go.Figure()

    # Loop through each exchange and add a line plot to the figure
    for exchange in exchanges:
        filtered_df = df[df['exchange'] == exchange]
        # sort in order of time
        filtered_df = filtered_df.sort_values(by=['participant_timestamp'])
        fig.add_trace(go.Scatter(x=filtered_df['participant_timestamp'], y=filtered_df['price'], mode='lines', name=f'Exchange {exchange}'))

    # Update layout
    fig.update_layout(title='Price vs. Time of Day (CST) for Multiple Exchanges', xaxis_title='Time of Day (CST)', yaxis_title='Price')

    # Show the plot
    fig.show()

def add_column_moving_average(df, column_name, window_size):
    df = df.copy()
    df[f'{column_name}_moving_average_{window_size}'] = df[column_name].rolling(window=window_size).mean()
    return df

def add_column_exponential_moving_average(df, column_name, window_size):
    df = df.copy()
    df[f'{column_name}_exponential_moving_average_{window_size}'] = df[column_name].ewm(span=window_size, adjust=False).mean()
    return df
def add_column_moving_average_convergence_divergence(df, column_name, window_size):
    df = df.copy()
    if f'{column_name}_exponential_moving_average_{window_size}' not in df.columns:
        df = add_column_exponential_moving_average(df, column_name, window_size)
    if f'{column_name}_exponential_moving_average_{window_size*2}' not in df.columns:
        df = add_column_exponential_moving_average(df, column_name, window_size*2)
    df[f'{column_name}_moving_average_convergence_divergence_{window_size}'] = df[f'{column_name}_exponential_moving_average_{window_size}'] - df[f'{column_name}_exponential_moving_average_{window_size*2}']
    return df
def add_column_bollinger_bands(df, column_name, window_size):
    if f'{column_name}_moving_average_{window_size}' not in df.columns:
        add_column_exponential_moving_average(df, column_name, window_size)
    df[f'{column_name}_bollinger_bands_upper_{window_size}'] = df[f'{column_name}_exponential_moving_average_{window_size}'] + 2 * df[column_name].rolling(window=window_size).std()
    df[f'{column_name}_bollinger_bands_lower_{window_size}'] = df[f'{column_name}_exponential_moving_average_{window_size}'] - 2 * df[column_name].rolling(window=window_size).std()

def add_column_vwap(df, price_column, volume_column, window_size):
    """
    Calculate the Volume Weighted Average Price (VWAP) over a specified rolling window.

    :param df: DataFrame containing the data.
    :param price_column: Name of the column containing price data.
    :param volume_column: Name of the column containing volume data.
    :param window_size: Size of the rolling window for VWAP calculation.
    :return: DataFrame with the VWAP values.
    """
    # Calculate the product of price and volume, and the cumulative sum of volume
    df['price_volume'] = df[price_column] * df[volume_column]
    df['cumulative_volume'] = df[volume_column].rolling(window=window_size).sum()
    df['cumulative_price_volume'] = df['price_volume'].rolling(window=window_size).sum()

    # Calculate VWAP
    df[f'vwap_{window_size}'] = df['cumulative_price_volume'] / df['cumulative_volume']
    df[f'vwap_{window_size}'] = df[f'vwap_{window_size}'].bfill()

    # Drop the intermediate columns
    df.drop(['price_volume', 'cumulative_volume', 'cumulative_price_volume'], axis=1, inplace=True)
    
    return df

def add_column_exponential_moving_variance(df, column_name, window_size):
    # AM: I think this is more relevant for volume because price doesnt change that much
    df = df.copy()
    ema = df[column_name].ewm(span=window_size, adjust=False).mean()
    squared_error = (df[column_name] - ema)**2
    df[f'{column_name}_exponential_moving_variance_{window_size}'] = squared_error.rolling(window=window_size).mean()
    df[f'{column_name}_exponential_moving_variance_{window_size}'] = df[f'{column_name}_exponential_moving_variance_{window_size}'].bfill()
    return df

    # ].ewm(span=span, adjust=False).mean()
# def add_column_relative_strength_index(df, column_name, window_size):

def add_rsi_column(df, price_column='price', periods=14, new_column_name='RSI'):
    df = df.copy()
    """
    Add a column of Relative Strength Index (RSI) to the DataFrame.

    :param df: Pandas DataFrame containing the price data.
    :param price_column: The name of the column that contains the price data.
    :param periods: Number of periods to use in the RSI calculation (default 14).
    :param new_column_name: The name of the new column for RSI values.
    :return: DataFrame with the RSI column added.
    """
    # Calculate price changes
    delta = df[price_column].diff()

    # Make two series: one for gains and the other for losses
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    # Use an expanding window for average gain and loss
    avg_gain = pd.Series(gain, index=df.index).expanding(min_periods=periods).mean()
    avg_loss = pd.Series(loss, index=df.index).expanding(min_periods=periods).mean()

    # Calculate the RS (Relative Strength)
    rs = (avg_gain / avg_loss).bfill()

    # Calculate the RSI
    rsi = 100 - (100 / (1 + rs))
 
    # Add RSI to the DataFrame
    df[new_column_name] = rsi
    # df[new_column_name] = df[new_column_name]
    
    return df

# def preprocessing(df):
    # Add a column for the 

def add_sinusoidal_time_encoding(df):
    df = df.copy()
    time = pd.to_datetime(df['participant_timestamp'], unit='ns')
    df.loc[:,'sin_time'] = np.sin(2*np.pi*time.dt.hour/24)
    df.loc[:,'cos_time'] = np.cos(2*np.pi*time.dt.hour/24)
    df.loc[:,'sin_minute'] = np.sin(2*np.pi*time.dt.minute/60)
    df.loc[:,'cos_minute'] = np.cos(2*np.pi*time.dt.minute/60)
    df.loc[:,'sin_second'] = np.sin(2*np.pi*time.dt.second/60)
    df.loc[:,'cos_second'] = np.cos(2*np.pi*time.dt.second/60)
    df.loc[:,'sin_day_of_week'] = np.sin(2*np.pi*time.dt.dayofweek/7)
    df.loc[:,'cos_day_of_week'] = np.cos(2*np.pi*time.dt.dayofweek/7)
    return df

def df_v_1(df, exchange = 3):
    df = get_df_exchange(df, exchange)
    df = add_sinusoidal_time_encoding(df)
    df['normalized_price'] = scaler_price.fit_transform(df[['price']])
    df['normalized_size'] = scaler_volume.fit_transform(df[['size']])
    df = add_column_exponential_moving_average(df, 'normalized_price', 5)
    df = add_column_exponential_moving_average(df, 'normalized_price', 20)
    df = add_column_exponential_moving_variance(df, 'normalized_price', 5)
    df = add_column_exponential_moving_variance(df, 'normalized_price', 20)
    df = add_column_exponential_moving_average(df, 'normalized_size', 5)
    df = add_column_exponential_moving_average(df, 'normalized_size', 20)
    df = add_column_vwap(df, 'normalized_price', 'normalized_size', 5)
    df = add_column_vwap(df, 'normalized_price', 'normalized_size', 20)
    df = add_rsi_column(df, 'normalized_price', 14, 'RSI')
    return df
    
def find_folder(folder_name, start_path):
    for root, dirs, files in os.walk(start_path):
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    return None


def get_df_exchange(df, exchange):
    return df[df['exchange'] == exchange]

if __name__ == "__main__":
    folder_name = 'group_02_project'
    start_path = os.path.expanduser('/media')  # Start search from the user's home directory
    folder_path = find_folder(folder_name, start_path)
    # df = pd.read_csv('/home/ashitabh/Documents/group_02_project/Polygon_API/polygon_data/TRADE_SPY_20230103_090000_to_20230103_235959.csv')
    df = pd.read_csv(f'{folder_path}/Polygon_API/polygon_data/TRADE_SPY_20230104_000000_to_20230104_235959.csv')
    df = df_v_1(df)
    print(df.columns)
    # df_3 = get_df_exchange(df, 3)
    # add_column_exponential_moving_average(df_3, 'price', 5)
    # add_column_bollinger_bands(df_3, 'price', 5)
    # calculate_vwap(df_3, 'price', 'size', 25)
    # calculate_vwap(df_3, 'price', 'size', 10)
    # columns_to_plot = ['price', 'price_exponential_moving_average_5', 'vwap','price_bollinger_bands_upper_5', 'price_bollinger_bands_lower_5']
    # columns_to_plot = ['price', 'price_exponential_moving_average_5', 'vwap_25', 'vwap_10']
    # make_plot(df_3, columns_to_plot, 'Price vs. Time of Day (CST) for Exchange NYSE')
    # make_plot(df_3, 'price', 'Price vs. Time of Day (CST) for Exchange NYSE')
    # make_plot_by_exchanges(df, [3])
