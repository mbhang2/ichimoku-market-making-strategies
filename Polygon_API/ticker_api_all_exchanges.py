from polygon import RESTClient
from convert_human_nanoseconds import datetime_to_nanoseconds, nanoseconds_to_datetime, add_to_timestamp, convert_milliseconds_to_nanoseconds
# Read API key from file
with open("api_key_git_ignore", "r") as f:
    api_key = f.read()
# Initialize REST client
client = RESTClient(api_key=api_key)
# Get the list of exchanges
exchanges = client.get_exchanges()
print(exchanges)

for exchange in exchanges:
    # print(type(exchange))
    # print(exchange.asset_class)
    if exchange.asset_class == 'stocks':
        print("Exchange ID: ", exchange.id)
        print("Exchange: ", exchange.name)