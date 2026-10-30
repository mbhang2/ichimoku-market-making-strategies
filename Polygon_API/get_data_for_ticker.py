from polygon import RESTClient
import requests
import pandas as pd
# import convert_human_nanoseconds from same folder 

from convert_human_nanosecond import datetime_to_nanoseconds, nanoseconds_to_datetime,  add_to_timestamp, convert_milliseconds_to_nanoseconds
# Read API key from file
with open("/home/ashitabh/Documents/group_02_project/api_key_git_ignore", "r") as f:
    api_key = f.read()
# Initialize REST client
client = RESTClient(api_key=api_key)


# set time limit in nano seconds

# START_TIME = '2023-01-03 09:00:00'
# END_TIME = '2023-01-04 12:00:00'

# START_TIME_NANO = datetime_to_nanoseconds(START_TIME)
# END_TIME_NANO = datetime_to_nanoseconds(END_TIME)

# print("START_TIME_NANO: ", START_TIME_NANO)
# print("END_TIME_NANO: ", END_TIME_NANO)

start_time = 1672704000000 # milliseconds
end_time = add_to_timestamp(start_time, hours=18)
start_time_nanoseconds = convert_milliseconds_to_nanoseconds(start_time)
start_time_nanoseconds = 1672756279839806693 + 1
end_time_nanoseconds = convert_milliseconds_to_nanoseconds(end_time)

print("start_time: ", start_time_nanoseconds)
print("end_time: ", end_time_nanoseconds)
print("start_time in human readable format: ", nanoseconds_to_datetime(start_time_nanoseconds))
print("end_time in human readable format: ", nanoseconds_to_datetime(end_time_nanoseconds))

API_string = f'https://api.polygon.io/v3/trades/AAPL?order=asc&limit=50000&sort=timestamp&timestamp.gte={start_time_nanoseconds}&timestamp.lt={end_time_nanoseconds}&apiKey={api_key}'


curr_df = None
while True:
    response = requests.get(API_string)
    json_response = response.json()
    # print("json_response: ", json_response)
    all_trades = json_response['results']
    curr_df = pd.DataFrame(all_trades)
    # print(curr_df)
    # print("0: sip_timestamp: ", curr_df['sip_timestamp'][0])
    print("0: participant_timestamp: ", curr_df['participant_timestamp'][0])
    print("len(curr_df): ", len(curr_df))
    # next_url = json_response['next_url']
    # print("Next URL: ", next_url)
    # if next_url is None:
    #     break
    # API_string = next_url
    
    break

# column names in curr_df
print(curr_df.columns)

# check if any empty values in participant_timestamp
# print("participant_timestamp: ", curr_df['participant_timestamp'].isnull().values.sum())
# print("sip_timestamp: ", curr_df['sip_timestamp'].isnull().values.sum())
# print("trf_timestamp: ", curr_df['trf_timestamp'].isnull().values.sum())


# get the last value of sip_timestamp
last_sip_timestamp = curr_df['sip_timestamp'].iloc[-1]
print("first_sip_timestamp: ", nanoseconds_to_datetime(curr_df['sip_timestamp'][0]))
print("last_sip_timestamp: ", nanoseconds_to_datetime(last_sip_timestamp))
print("last sip time in nanoseconds: ", last_sip_timestamp)

print("first_participant_timestamp: ", nanoseconds_to_datetime(curr_df['participant_timestamp'][0]))
print("last_participant_timestamp: ", nanoseconds_to_datetime(curr_df['participant_timestamp'].iloc[-1]))

# response = requests.get(API_string)

# print(type(response))
# json_response = response.json()
# print(type(json_response))

# print(json_response)

# print first 5 elements of json_response
# for key, value in json_response.items():
#     if key == 'results':
#         print(type(value))
#         df = pd.DataFrame(value[0:2])
#         print(df)
#         break
#     print(key, ":", value)
#     print("")