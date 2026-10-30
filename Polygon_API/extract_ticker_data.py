#from polygon import RESTClient
#import requests
#import pandas as pd
#from convert_human_nanosecond import datetime_to_nanoseconds, nanoseconds_to_datetime,  add_to_timestamp, convert_milliseconds_to_nanoseconds
#from tqdm import tqdm
#import logging
#from multiprocessing import Pool
#import os
import subprocess
import pkg_resources
import sys
required_modules = ["requests", "polygon","pandas","convert_human_nanosecond", "tqdm", "logging", "multiprocessing", "os"]

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for module in required_modules:
    try:
        # Try importing the module
        pkg_resources.require(module)
    except pkg_resources.DistributionNotFound:
        # If the module is not found, install it
        print(f"Installing {module}")
        install(module)
    except pkg_resources.VersionConflict:
        # If there's a version conflict, you can handle it here
        # For simplicity, we'll just print a message
        print(f"Version conflict detected for {module}. Please check the required version.")
    else:
        print(f"{module} is already installed.")

print("All modules are installed.")

with open("/home/ashitabh/Documents/group_02_project/api_key_git_ignore", "r") as f:
    api_key = f.read()

client = RESTClient(api_key=api_key)

ticker = 'SPY'
logging.basicConfig(filename='./polygon_data_parse.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def get_start_end_time_list(start_time,num_days):
    '''
    start_time: in milliseconds
    num_days: number of days to get data for
    '''
    DAY_IN_UTC = 86400000 # 24 hours in milliseconds
    start_time_list = []
    end_time_list = []
    for i in range(num_days):
        start_time_list.append(start_time + i * DAY_IN_UTC)
        end_time_list.append(start_time + (i+1) * DAY_IN_UTC)
    return list(zip(start_time_list, end_time_list))

def get_API_string(ticker, start_time, end_time = None):

    if start_time is None:
        raise ValueError("start_time cannot be None")
    if end_time is not None and end_time < start_time:
        raise ValueError("end_time cannot be less than start_time")
    if end_time is not None and end_time == start_time:
        raise ValueError("end_time cannot be equal to start_time")
    if ticker is None:
        raise ValueError("ticker cannot be None")
    
    if end_time is None:
        API_string = f'https://api.polygon.io/v3/trades/{ticker}?order=asc&limit=50000&sort=timestamp&timestamp.gte={start_time}&apiKey={api_key}'
        return API_string
    else:
        API_string = f'https://api.polygon.io/v3/trades/{ticker}?order=asc&limit=50000&sort=timestamp&timestamp.gte={start_time}&timestamp.lt={end_time}&apiKey={api_key}'
        return API_string


def make_request(ticker, START_TIME_IN_NANOSECONDS, END_TIME_IN_NANOSECONDS):
    '''
    Function to make a request and return a pandas DataFrame.
    The DataFrame includes various trade-related columns.
    '''
    main_df = pd.DataFrame(columns=['conditions', 'exchange', 'id', 'participant_timestamp', 'price',
       'sequence_number', 'sip_timestamp', 'size', 'tape', 'trf_id',
       'trf_timestamp'])
    API_String = get_API_string(ticker, START_TIME_IN_NANOSECONDS, END_TIME_IN_NANOSECONDS)
    current_start_time = START_TIME_IN_NANOSECONDS
    final_end_time = END_TIME_IN_NANOSECONDS
    current_end_time = final_end_time
    print(nanoseconds_to_datetime(current_start_time))
    # print("final_end_time - current_start_time: ", final_end_time - current_start_time)
    if API_String is None:
        logging.error("API_String cannot be None")
        raise ValueError("API_String cannot be None")
    counter = 0
    while True:
        counter += 1
        logging.info("*" * 50)
        logging.info(f"Current start time: {nanoseconds_to_datetime(current_start_time)}")
        logging.info(f"Current start time(ns): {current_start_time}")
        logging.info(f"Current end time: {nanoseconds_to_datetime(current_end_time)}")
        logging.info(f"Final end time: {nanoseconds_to_datetime(final_end_time)}")
        logging.info("*" * 25)
        response = requests.get(API_String)
        json_response = response.json()
        if len(json_response['results']) == 0:
            print("len(json_response['results']) == 0")
            break
        if current_start_time >= current_end_time:
            print("current_start_time >= current_end_time")
            break
        all_trades = json_response['results']
        curr_df = pd.DataFrame(all_trades)
        # print("length curr_df: ", len(curr_df))
        # if counter > 4:
        #     break
        if current_start_time == curr_df['participant_timestamp'].iloc[-1]:
            print("current_start_time == curr_df['participant_timestamp'].iloc[-1]")
            break
        main_df = pd.concat([main_df, curr_df])
        current_start_time = curr_df['participant_timestamp'].iloc[-1]
        current_end_time = final_end_time
        API_String = get_API_string(ticker, current_start_time, current_end_time)
        logging.info(f"Number of rows in curr_df: {len(curr_df)}")
        logging.info(f"Number of rows in main_df: {len(main_df)}")
        logging.info(f"First time in current df: {nanoseconds_to_datetime(curr_df['participant_timestamp'][0])}")
        logging.info(f"Last time in current df: {nanoseconds_to_datetime(curr_df['participant_timestamp'].iloc[-1])}")
        logging.info("*" * 50)

    return main_df

# def make_request(ticker, START_TIME_IN_NANOSECONDS, END_TIME_IN_NANOSECONDS):
#     '''
#     pandas dataframe to store all trades ['conditions', 'exchange', 'id', 'participant_timestamp', 'price',
#        'sequence_number', 'sip_timestamp', 'size', 'tape', 'trf_id',
#        'trf_timestamp']
#     '''
#     main_df = pd.DataFrame(columns=['conditions', 'exchange', 'id', 'participant_timestamp', 'price',
#        'sequence_number', 'sip_timestamp', 'size', 'tape', 'trf_id',
#        'trf_timestamp'])
#     API_String = get_API_string(ticker, START_TIME_IN_NANOSECONDS, END_TIME_IN_NANOSECONDS)
#     current_start_time = START_TIME_IN_NANOSECONDS
#     final_end_time = END_TIME_IN_NANOSECONDS
#     current_end_time = final_end_time
#     if API_String is None:
#         raise ValueError("API_String cannot be None")
#     counter = 0
#     while True:
#         counter += 1
#         print("*"*50)
#         # print("Status code: ", response.status_code)
#         print("Current start time: ", nanoseconds_to_datetime(current_start_time))
#         print("Current start time(ns): ", current_start_time)
#         print("Current end time: ", nanoseconds_to_datetime(current_end_time))
#         print("Final end time: ", nanoseconds_to_datetime(final_end_time))
#         print("*"*25)
#         response = requests.get(API_String)
#         json_response = response.json()
#         if len(json_response['results']) == 0:
#             break
#         if current_start_time >= current_end_time:
#             break
#         all_trades = json_response['results']
#         curr_df = pd.DataFrame(all_trades)
#         if counter > 4:
#             break
#         if len(curr_df) == 2:
#             print("curr_df: ", curr_df)
#         if current_start_time == curr_df['participant_timestamp'].iloc[-1]:
#             break
#         main_df = pd.concat([main_df, curr_df])
#         current_start_time = curr_df['participant_timestamp'].iloc[-1]
#         current_end_time = final_end_time
#         API_String = get_API_string(ticker, current_start_time, current_end_time)
#         print("Number of rows in curr_df: ", len(curr_df))
#         print("Number of rows in main_df: ", len(main_df))
#         #start time in current df
#         print("First time in current df: ", nanoseconds_to_datetime(curr_df['participant_timestamp'][0]))
#         print("First time in (ns) current df: ", curr_df['participant_timestamp'][0])
#         #last time in current df
#         print("Last time in current df: ", nanoseconds_to_datetime(curr_df['participant_timestamp'].iloc[-1]))
#         print("Last time in (ns) current df: ", curr_df['participant_timestamp'].iloc[-1])
#         print("*"*50)
    
#     return main_df


def savetocsv(df, ticker = 'SPY'):
    # get the first participant_timestamp
    if len(df) == 0:
        print("df is empty")
        return
    # print("Length of df: ", len(df))
    # print("HEAD")
    first_participant_timestamp = df['participant_timestamp'].iloc[0]
    last_participant_timestamp = df['participant_timestamp'].iloc[-1]
    
    # print(df.head())
    first_participant_timestamp = nanoseconds_to_datetime(first_participant_timestamp, filename=True)
    last_participant_timestamp = nanoseconds_to_datetime(last_participant_timestamp, filename=True)

    print("first_participant_timestamp: ", first_participant_timestamp)
    print("last_participant_timestamp: ", last_participant_timestamp)

    filename = f"TRADE_{ticker}_{first_participant_timestamp}_to_{last_participant_timestamp}.csv"

    dir_path = "Polygon_API/polygon_data/"

    full_filename = dir_path + filename

    # overwrite the file if it already exists
    df.to_csv(full_filename, index=False,na_rep='NaN')
    print(f"Saved to csv - filename: {filename}")


def convert_list_int_to_str(df):
    '''
    Convert list of integers to string with ; as separator
    '''
    df['conditions'] = df['conditions'].apply(lambda x: ';'.join(map(str, x)) if isinstance(x, list) else x)
    return df

'''
convert [(time_in_milliseconds, time_in_milliseconds), (time_in_milliseconds, time_in_milliseconds)] to [(time_in_nanoseconds, time_in_nanoseconds), (time_in_nanoseconds, time_in_nanoseconds)]
'''
def convert_list_milliseconds_to_nanoseconds(list_of_tuples):
    list_in_ns = []
    for start_time, end_time in list_of_tuples:
        list_in_ns.append((convert_milliseconds_to_nanoseconds(start_time), convert_milliseconds_to_nanoseconds(end_time)))
    return list_in_ns


def process_day_range(day_range):
    start_time, end_time = day_range
    logging.info(f"start_time: {nanoseconds_to_datetime(start_time)}")
    logging.info(f"end_time: {nanoseconds_to_datetime(end_time)}")
    main_df = make_request('SPY', start_time, end_time)
    main_df = convert_list_int_to_str(main_df)
    savetocsv(main_df, ticker='SPY')
    return f"Done: {nanoseconds_to_datetime(start_time)} to {nanoseconds_to_datetime(end_time)}"

if __name__ == "__main__":
    
    # START_TIME_IN_MILLISECONDS = 1672704000000 # milliseconds 2023-01-03 00:00:00
    START_TIME_IN_MILLISECONDS = 1671429600000
    all_days_start_end_list = get_start_end_time_list(START_TIME_IN_MILLISECONDS, 33)
    all_days_start_end_list = convert_list_milliseconds_to_nanoseconds(all_days_start_end_list)

    # check if polygon_data folder exists
    if not os.path.exists("Polygon_API/polygon_data"):
        print("All directories in current directory: ", os.listdir(".") )
        print("polygon_data folder does not exist")
        raise ValueError("polygon_data folder does not exist")
    
    with Pool() as pool:
        results = list(tqdm(pool.imap(process_day_range, all_days_start_end_list), total=len(all_days_start_end_list), desc="Processing Days"))

    
    
    
    # fifth_day = [all_days_start_end_list[5]]
    # for start_time, end_time in tqdm(all_days_start_end_list, desc="Processing Days"):
    #     # print("start_time: ", nanoseconds_to_datetime(start_time))
    #     # print("end_time: ", nanoseconds_to_datetime(end_time))
    #     logging.info(f"start_time: {nanoseconds_to_datetime(start_time)}")
    #     logging.info(f"end_time: {nanoseconds_to_datetime(end_time)}")
    #     main_df = make_request('SPY', start_time, end_time)
    #     main_df = convert_list_int_to_str(main_df)
    #     savetocsv(main_df, ticker='SPY')
    #     print("Done")


    
    
    # print("all_days_start_end_list: ", all_days_start_end_list)
    # print("START_TIME_IN_NANOSECONDS: ", START_TIME_IN_NANOSECONDS)
    # print("START TIME in human readable format: ", nanoseconds_to_datetime(START_TIME_IN_NANOSECONDS))
    # print("END_TIME_IN_NANOSECONDS: ", END_TIME_IN_NANOSECONDS)
    # print("END TIME in human readable format: ", nanoseconds_to_datetime(END_TIME_IN_NANOSECONDS))
    # main_df = make_request('SPY')
    # main_df = convert_list_int_to_str(main_df)
    # print("Testing: ", main_df['conditions'].iloc[1])
    # # main_df['conditions'] = main_df['conditions'].apply(lambda x: ';'.join(map(str, x)))
    # print("Number of rows in main_df: ", len(main_df))
    # # expected memory usage of dataframe in megabytes
    # print("Expected memory usage of dataframe: ", main_df.memory_usage(deep=True).sum() / 1024 ** 2)
    # print("Parsing Done")
    # savetocsv(main_df, ticker='SPY')
    # print("Done")



