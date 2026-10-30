import os
import pandas as pd


# Converts string timestamp to pandas timestamp
def to_timestamp(input):
    time = input.split(" ")
    return pd.to_datetime(time[0] + 'T' + time[1] + 'Z', format='%Y-%m-%dT%H:%M:%S.%fZ')


def to_date(input):
    return pd.to_datetime(input, format='%Y%m%d')


def date_to_string(input):
    year = str(input.year)
    month = str(input.month) if input.month >= 10 else f"0{input.month}"
    day = str(input.day) if input.day >= 10 else f"0{input.day}"

    return year+month+day


# reads the file and returns pandas dataframe with columns of [collection time, price, size]
def read_tick_file(file_name):
    if not((os.path.isfile(file_name)) and os.access(file_name, os.R_OK)):
        print("ERROR: File not found")
        return None

    data_list = []
    with open(file_name, 'r') as file:
        for row in file: # each row has format of string of 'collection time, source time, sequence number, tick type, market center, price, size'
            row_list = row.split(',')

            data_list.append([to_timestamp(row_list[0]),float(row_list[5]), int(row_list[6][0:-1])])
    df = pd.DataFrame(data_list, columns=['Collection time', 'Price', 'Size'])
    return df


def read_date_range_tick_file(ticker, start_date, end_date):
    data = {}

    date = to_date(start_date)

    while date != to_date(end_date)+pd.Timedelta(days=1):
        file_name = f"Analytics/IEX/Sample_Data/{ticker.upper()}/{ticker.upper()}_{date_to_string(date)}.txt"

        if (os.path.isfile(file_name)) and os.access(file_name, os.R_OK):
            data[date] = read_tick_file(file_name)

        date += pd.Timedelta(days=1)

    return data

