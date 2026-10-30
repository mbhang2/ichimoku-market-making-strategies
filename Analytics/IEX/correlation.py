import numpy as np
import pandas as pd
import file_parser


"""
Computes weighted average price between two timestamps.

@param Timestamp timestamp1 - earlier timestamp
@param Timestamp timestamp2 - later timestamp
@param Timestamp timestamp3 - timestamp which we would like to compute the weighted average price
@param float price1 - price at timestamp1
@param float price2 - price at timestamp2

@return the weighted average price at timestamp3
"""
def weighted_average_price(timestamp1, timestamp2, timestamp3, price1, price2):
    slope = (price2 - price1)/((timestamp2-timestamp1)/pd.Timedelta(seconds=1))

    return price1 + slope * ((timestamp3 - timestamp1)/pd.Timedelta(seconds=1))


"""
Computes correlation coefficient of two tickers on a given date.

Two ticker data have different timestamp, so we will resolve this by combining timestamp and computing the price.

For example, if ticker1 has timestamp [1,3,5] and ticker2 has that of [2,4,6], combined timestamp for both tickers will be [1,2,3,4,5,6].
Price of ticker1 at timestamp [2] will be the weighted average of price at timestamp [1] and [3].

While computing the correlation coefficient, for accuracy, the correlation coefficient will be computed starting from the later starting timestamp
and to earlier ending timestamp.

@param str ticker1 - Ticker of the first security
@param str ticker2 - Ticker of the second security
@param str date - Date in format of "YYYYMMDD"
@param int kwargs - round to certain number of digits (optional)

@return the correlation coefficient between the two tickers on a certain date

Ex. pair_correlation("SPY", "QQQ", "20191001", round=3)
"""
def pair_correlation(ticker1, ticker2, date, **kwargs):
    ticker1_data = file_parser.read_tick_file(f"Analytics/IEX/Sample_Data/{ticker1.upper()}/{ticker1.upper()}_{date}.txt")
    ticker2_data = file_parser.read_tick_file(f"Analytics/IEX/Sample_Data/{ticker2.upper()}/{ticker2.upper()}_{date}.txt")

    if ticker1_data.empty or ticker2_data.empty:
        return

    round_int = int(kwargs.get('round', 2))

    # Combine timestamp for both tickers
    # Drop unnecessary data at the front
    ticker1_start, ticker2_start = False, False
    while True:
        if ticker1_data["Collection time"][0] < ticker2_data["Collection time"][1]: # ticker1 timestamp starts first
            ticker1_start = True
            if ticker1_start and ticker2_start:
                break
            ticker1_data = ticker1_data.iloc[1:]
            ticker1_data.reset_index(drop=True, inplace=True)
            
        else: # ticker2 timestamp starts first
            ticker2_start = True
            if ticker1_start and ticker2_start:
                break
            ticker2_data = ticker2_data.iloc[1:]
            ticker2_data.reset_index(drop=True, inplace=True)

    #Drop unnecessary data at the back
    ticker1_end, ticker2_end = False, False
    while True:
        if ticker1_data["Collection time"][len(ticker1_data)-1] < ticker2_data["Collection time"][len(ticker2_data)-1]: # ticker1 timestamp ends first
            ticker1_end = True
            if ticker1_end and ticker2_end:
                break
            ticker2_data = ticker2_data.iloc[:-1]
            ticker2_data.reset_index(drop=True, inplace=True)

        else: # ticker2 timestamp ends first
            ticker2_end = True
            if ticker1_end and ticker2_end:
                break
            ticker1_data = ticker1_data.iloc[:-1]
            ticker1_data.reset_index(drop=True, inplace=True)

    # Combine
    ticker1_data["Added"] = 0
    ticker2_data["Added"] = 0
    ticker1_pointer, ticker2_pointer = 0, 0
    ticker1_data_original_length = len(ticker1_data)
    ticker2_data_original_length = len(ticker2_data)
 
    while ticker1_pointer < ticker1_data_original_length or ticker2_pointer < ticker2_data_original_length:
        # Starting case
        if ticker1_pointer == 0 and ticker2_pointer == 0:
            if ticker1_data["Collection time"][0] < ticker2_data["Collection time"][0]:
                ticker2_data.loc[len(ticker2_data)] = [ticker1_data["Collection time"][0], weighted_average_price(ticker2_data["Collection time"][0], 
                                                        ticker2_data["Collection time"][1], ticker1_data["Collection time"][0], ticker2_data["Price"][0], 
                                                        ticker2_data["Price"][1]), np.NaN, 1]
                ticker1_pointer += 1
                continue
            else:
                ticker1_data.loc[len(ticker1_data)] = [ticker2_data["Collection time"][0], weighted_average_price(ticker1_data["Collection time"][0], 
                                                        ticker1_data["Collection time"][1], ticker2_data["Collection time"][0], ticker1_data["Price"][0], 
                                                        ticker1_data["Price"][1]), np.NaN, 1]
                ticker2_pointer += 1
                continue

        # Ending case
        if ticker1_pointer == ticker1_data_original_length:
            ticker1_data.loc[len(ticker1_data)] = [ticker2_data["Collection time"][ticker2_pointer], weighted_average_price(ticker1_data["Collection time"][ticker1_pointer-2],
                                                    ticker1_data["Collection time"][ticker1_pointer - 1], ticker2_data["Collection time"][ticker2_pointer],
                                                    ticker1_data["Price"][ticker1_pointer - 2], ticker1_data["Price"][ticker1_pointer - 1]), np.NAN, 1]
            ticker2_pointer += 1
            continue

        if ticker2_pointer == ticker2_data_original_length:
            ticker2_data.loc[len(ticker2_data)] = [ticker1_data["Collection time"][ticker1_pointer], weighted_average_price(ticker2_data["Collection time"][ticker2_pointer-2],
                                                    ticker2_data["Collection time"][ticker2_pointer - 1], ticker1_data["Collection time"][ticker1_pointer],
                                                    ticker2_data["Price"][ticker2_pointer - 2], ticker2_data["Price"][ticker2_pointer - 1]), np.NAN, 1]
            ticker1_pointer += 1
            continue

        # General case
        if ticker1_data["Collection time"][ticker1_pointer] < ticker2_data["Collection time"][ticker2_pointer]:
            if ticker2_pointer == 0:
                ticker2_data.loc[len(ticker2_data)] = [ticker1_data["Collection time"][ticker1_pointer], weighted_average_price(ticker2_data["Collection time"][ticker2_pointer],
                                                    ticker2_data["Collection time"][ticker2_pointer+1], ticker1_data["Collection time"][ticker1_pointer],
                                                    ticker2_data["Price"][ticker2_pointer], ticker2_data["Price"][ticker2_pointer+1]), np.NaN, 1]

            else:
                ticker2_data.loc[len(ticker2_data)] = [ticker1_data["Collection time"][ticker1_pointer], weighted_average_price(ticker2_data["Collection time"][ticker2_pointer-1],
                                                    ticker2_data["Collection time"][ticker2_pointer], ticker1_data["Collection time"][ticker1_pointer],
                                                    ticker2_data["Price"][ticker2_pointer-1], ticker2_data["Price"][ticker2_pointer]), np.NaN, 1]
            ticker1_pointer += 1
            continue
        else:
            if ticker1_pointer == 0:
                ticker1_data.loc[len(ticker1_data)] = [ticker2_data["Collection time"][ticker2_pointer], weighted_average_price(ticker1_data["Collection time"][ticker1_pointer],
                                                    ticker1_data["Collection time"][ticker1_pointer+1], ticker2_data["Collection time"][ticker2_pointer],
                                                    ticker1_data["Price"][ticker1_pointer], ticker1_data["Price"][ticker1_pointer+1]), np.NaN, 1]

            else:
                ticker1_data.loc[len(ticker1_data)] = [ticker2_data["Collection time"][ticker2_pointer], weighted_average_price(ticker1_data["Collection time"][ticker1_pointer-1],
                                                    ticker1_data["Collection time"][ticker1_pointer], ticker2_data["Collection time"][ticker2_pointer],
                                                    ticker1_data["Price"][ticker1_pointer-1], ticker1_data["Price"][ticker1_pointer]), np.NaN, 1]
            ticker2_pointer += 1
            continue

    
    ticker1_data = ticker1_data.sort_values(by=['Collection time'])
    ticker1_data.reset_index(drop=True, inplace=True)
    ticker1_data = ticker1_data.rename(columns={"Price": f"{ticker1} price"})

    ticker2_data = ticker2_data.sort_values(by=['Collection time'])
    ticker2_data.reset_index(drop=True, inplace=True)
    ticker2_data = ticker2_data.rename(columns={"Price": f"{ticker2} price"})

    return round(pd.concat([ticker1_data[f"{ticker1} price"], ticker2_data[f"{ticker2} price"]], axis=1).corr()[f"{ticker1} price"][f"{ticker2} price"], round_int)

"""
Helper function computing the correlation coefficient

@param str ticker1 - Ticker of the first security
@param str ticker2 - Ticker of the second security
@param DataFrame ticker1_data - dataframe for the first ticker
@param DataFrame ticker2_data - dataframe for the second ticker
@param int kwargs - round to certain number of digits (optional)

@return the correlation coefficient between the two tickers on a certain date
"""
def pair_correlation_helper(ticker1, ticker2, ticker1_data, ticker2_data, **kwargs):
    round_int = int(kwargs.get('round', 2))
    ticker1_start, ticker2_start = False, False
    while True:
        if ticker1_data["Collection time"][0] < ticker2_data["Collection time"][1]: # ticker1 timestamp starts first
            ticker1_start = True
            if ticker1_start and ticker2_start:
                break
            ticker1_data = ticker1_data.iloc[1:]
            ticker1_data.reset_index(drop=True, inplace=True)
            
        else: # ticker2 timestamp starts first
            ticker2_start = True
            if ticker1_start and ticker2_start:
                break
            ticker2_data = ticker2_data.iloc[1:]
            ticker2_data.reset_index(drop=True, inplace=True)

    #Drop unnecessary data at the back
    ticker1_end, ticker2_end = False, False
    while True:
        if ticker1_data["Collection time"][len(ticker1_data)-1] < ticker2_data["Collection time"][len(ticker2_data)-1]: # ticker1 timestamp ends first
            ticker1_end = True
            if ticker1_end and ticker2_end:
                break
            ticker2_data = ticker2_data.iloc[:-1]
            ticker2_data.reset_index(drop=True, inplace=True)

        else: # ticker2 timestamp ends first
            ticker2_end = True
            if ticker1_end and ticker2_end:
                break
            ticker1_data = ticker1_data.iloc[:-1]
            ticker1_data.reset_index(drop=True, inplace=True)

    # Combine
    ticker1_data["Added"] = 0
    ticker2_data["Added"] = 0
    ticker1_pointer, ticker2_pointer = 0, 0
    ticker1_data_original_length = len(ticker1_data)
    ticker2_data_original_length = len(ticker2_data)
 
    while ticker1_pointer < ticker1_data_original_length or ticker2_pointer < ticker2_data_original_length:
        # Starting case
        if ticker1_pointer == 0 and ticker2_pointer == 0:
            if ticker1_data["Collection time"][0] < ticker2_data["Collection time"][0]:
                ticker2_data.loc[len(ticker2_data)] = [ticker1_data["Collection time"][0], weighted_average_price(ticker2_data["Collection time"][0], 
                                                        ticker2_data["Collection time"][1], ticker1_data["Collection time"][0], ticker2_data["Price"][0], 
                                                        ticker2_data["Price"][1]), np.NaN, 1]
                ticker1_pointer += 1
                continue
            else:
                ticker1_data.loc[len(ticker1_data)] = [ticker2_data["Collection time"][0], weighted_average_price(ticker1_data["Collection time"][0], 
                                                        ticker1_data["Collection time"][1], ticker2_data["Collection time"][0], ticker1_data["Price"][0], 
                                                        ticker1_data["Price"][1]), np.NaN, 1]
                ticker2_pointer += 1
                continue

        # Ending case
        if ticker1_pointer == ticker1_data_original_length:
            ticker1_data.loc[len(ticker1_data)] = [ticker2_data["Collection time"][ticker2_pointer], weighted_average_price(ticker1_data["Collection time"][ticker1_pointer-2],
                                                    ticker1_data["Collection time"][ticker1_pointer - 1], ticker2_data["Collection time"][ticker2_pointer],
                                                    ticker1_data["Price"][ticker1_pointer - 2], ticker1_data["Price"][ticker1_pointer - 1]), np.NAN, 1]
            ticker2_pointer += 1
            continue

        if ticker2_pointer == ticker2_data_original_length:
            ticker2_data.loc[len(ticker2_data)] = [ticker1_data["Collection time"][ticker1_pointer], weighted_average_price(ticker2_data["Collection time"][ticker2_pointer-2],
                                                    ticker2_data["Collection time"][ticker2_pointer - 1], ticker1_data["Collection time"][ticker1_pointer],
                                                    ticker2_data["Price"][ticker2_pointer - 2], ticker2_data["Price"][ticker2_pointer - 1]), np.NAN, 1]
            ticker1_pointer += 1
            continue

        # General case
        if ticker1_data["Collection time"][ticker1_pointer] < ticker2_data["Collection time"][ticker2_pointer]:
            if ticker2_pointer == 0:
                ticker2_data.loc[len(ticker2_data)] = [ticker1_data["Collection time"][ticker1_pointer], weighted_average_price(ticker2_data["Collection time"][ticker2_pointer],
                                                    ticker2_data["Collection time"][ticker2_pointer+1], ticker1_data["Collection time"][ticker1_pointer],
                                                    ticker2_data["Price"][ticker2_pointer], ticker2_data["Price"][ticker2_pointer+1]), np.NaN, 1]

            else:
                ticker2_data.loc[len(ticker2_data)] = [ticker1_data["Collection time"][ticker1_pointer], weighted_average_price(ticker2_data["Collection time"][ticker2_pointer-1],
                                                    ticker2_data["Collection time"][ticker2_pointer], ticker1_data["Collection time"][ticker1_pointer],
                                                    ticker2_data["Price"][ticker2_pointer-1], ticker2_data["Price"][ticker2_pointer]), np.NaN, 1]
            ticker1_pointer += 1
            continue
        else:
            if ticker1_pointer == 0:
                ticker1_data.loc[len(ticker1_data)] = [ticker2_data["Collection time"][ticker2_pointer], weighted_average_price(ticker1_data["Collection time"][ticker1_pointer],
                                                    ticker1_data["Collection time"][ticker1_pointer+1], ticker2_data["Collection time"][ticker2_pointer],
                                                    ticker1_data["Price"][ticker1_pointer], ticker1_data["Price"][ticker1_pointer+1]), np.NaN, 1]

            else:
                ticker1_data.loc[len(ticker1_data)] = [ticker2_data["Collection time"][ticker2_pointer], weighted_average_price(ticker1_data["Collection time"][ticker1_pointer-1],
                                                    ticker1_data["Collection time"][ticker1_pointer], ticker2_data["Collection time"][ticker2_pointer],
                                                    ticker1_data["Price"][ticker1_pointer-1], ticker1_data["Price"][ticker1_pointer]), np.NaN, 1]
            ticker2_pointer += 1
            continue
    
    ticker1_data = ticker1_data.sort_values(by=['Collection time'])
    ticker1_data.reset_index(drop=True, inplace=True)
    ticker1_data = ticker1_data.rename(columns={"Price": f"{ticker1} price"})

    ticker2_data = ticker2_data.sort_values(by=['Collection time'])
    ticker2_data.reset_index(drop=True, inplace=True)
    ticker2_data = ticker2_data.rename(columns={"Price": f"{ticker2} price"})

    # print("Parsed data: \n")
    # print(ticker2_data)

    return round(pd.concat([ticker1_data[f"{ticker1} price"], ticker2_data[f"{ticker2} price"]], axis=1).corr()[f"{ticker1} price"][f"{ticker2} price"], round_int)

"""
Computes correlation matrix of multiple tickers on a given date.

@param str date - Date in format of "YYYYMMDD"
@param str ticker1 - Ticker of the first security
@param str ticker2 - Ticker of the second security
@param str argv - additional tickers
@param int kwargs - round to certain number of digits (optional)

@return the correlation matrix between the multiple tickers on a certain date

Ex. multiple_correlation("20191001", "AAPL", "AMZN", "SPY", "QQQ", "TLT", round=3)
"""
def multiple_correlation(date, ticker1, ticker2, *argv, **kwargs):
    tickers_set = {ticker1.upper(), ticker2.upper()}
    for tickers in argv:
        tickers_set.add(tickers.upper())

    round_int = int(kwargs.get('round', 2))

    correlation_matrix = pd.DataFrame(columns=sorted(tickers_set), dtype='float64')

    for i in sorted(tickers_set):
        correlation_matrix.loc[i] = [1.0]*len(tickers_set)

        for j in sorted(tickers_set):
            if i < j:
                correlation_matrix.at[i,j] = round(pair_correlation(i, j ,date), round_int)
            elif i > j:
                correlation_matrix.at[i,j] = correlation_matrix.at[j,i]
    
    return correlation_matrix


"""
Computes the effect of shifting timestamp by certain increment to determine high-frequency lead-lag relationship

@param str ticker1 - Ticker of the first security
@param str ticker2 - Ticker of the second security
@param str date - Date in format of "YYYYMMDD"
@param int kwargs - time increment in nanoseconds (optional)

@return the dataframe of "time shifted" vs "correlation"

Ex. pair_TLCC("AAPL", "AMZN", "20191001", increment=100)
"""
def pair_TLCC(ticker1, ticker2, date, **kwargs):
    window = kwargs.get('window', 50000) # test time window in nanoseconds
    increment_nano = kwargs.get('increment', 100) # time increment in nanoseconds
    offset = -int(window/increment_nano)

    # print(f"TLCC Test with window: {window/1000} microseconds and increment of {increment_nano/1000} microseconds")

    ticker1_data = file_parser.read_tick_file(f"Analytics/IEX/Sample_Data/{ticker1.upper()}/{ticker1.upper()}_{date}.txt")
    ticker2_data = file_parser.read_tick_file(f"Analytics/IEX/Sample_Data/{ticker2.upper()}/{ticker2.upper()}_{date}.txt")

    if ticker1_data.empty or ticker2_data.empty:
        return

    ticker2_data["Collection time"] = ticker2_data["Collection time"] - pd.Timedelta(microseconds=np.abs(offset)*increment_nano/1000)

    tlcc = pd.DataFrame(columns=[f"Offset ({increment_nano/1000} µs)", "Correlation coefficient"], dtype='float64')
    tlcc = tlcc.set_index(f"Offset ({increment_nano/1000} µs)")

    for i in range(-2*offset+1):
        # print(offset)
        corr = pair_correlation_helper(ticker1, ticker2, ticker1_data.copy(deep=True), ticker2_data.copy(deep=True), round=5)
        # print(f"corr: {corr}")
        # print("\n####################################################################\n")

        tlcc.loc[offset] = [corr]

        ticker2_data["Collection time"] = ticker2_data["Collection time"] + pd.Timedelta(microseconds=increment_nano/1000)
        offset += 1

    print(tlcc)

    return tlcc