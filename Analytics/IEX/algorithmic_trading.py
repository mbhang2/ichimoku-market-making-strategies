import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import file_parser


def moving_average_strategy(ticker, date, short, long, **kwargs):
    data = file_parser.read_tick_file(f"Analytics/IEX/Sample_Data/{ticker.upper()}/{ticker.upper()}_{date}.txt")

    if len(data) == 0:
        return

    data["Short MA"] = np.NAN
    data["Long MA"] = np.NAN

    short_list = [np.NAN]*short
    long_list = [np.NAN]*long

    position = 0
    buying_price = 0.0
    selling_price = 0.0
    pnl_list = []
    cumulative_pnl = []

    for i in range(len(data)):
        short_ma, long_ma = np.NAN, np.NAN
        price = data["Price"][i]

        # Updating moving average list
        del short_list[0]
        short_list.append(price)
        del long_list[0]
        long_list.append(price)

        if i-1 >= short:
            short_ma = np.mean(short_list)
            data.at[i, "Short MA"] = short_ma

        if i-1 >= long:
            long_ma = np.mean(long_list)
            data.at[i, "Long MA"] = long_ma

            if short_ma > long_ma and data["Short MA"][i-1] < data["Long MA"][i-1]:
                buying_price = data["Price"][i]
                # print(f"Buy at {buying_price}")
                if position == 0:
                    position += 1
                else:
                    position += 2
                    pnl_list.append(round((selling_price-buying_price)*100/selling_price, 2))

            if short_ma < long_ma and data["Short MA"][i-1] > data["Long MA"][i-1] and position > 0:
                selling_price = data["Price"][i]
                # print(f"Sell at {selling_price}")

                if position == 0:
                    position -= 1
                else:
                    position -= 2
                    pnl_list.append(round((selling_price-buying_price)*100/buying_price, 2))

    # Close at end of day
    if position > 0:
        selling_price = data["Price"][len(data)-1]
        pnl_list.append(round((selling_price-buying_price)*100/buying_price, 2))
    elif position < 0:
        buying_price = data["Price"][len(data)-1]
        pnl_list.append(round((selling_price-buying_price)*100/selling_price, 2))

    position = 0

    for i in pnl_list:
        if len(cumulative_pnl) == 0:
            cumulative_pnl.append(i)
        else:
            cumulative_pnl.append(cumulative_pnl[-1]+i)

    plt.plot(cumulative_pnl)
    plt.title("Cumulative P&L")
    plt.xlabel("Trades")
    plt.ylabel("Profit (%)")
    plt.show()

    return (pnl_list, cumulative_pnl)


def multi_day_moving_average_strategy(ticker, start_date, end_date, short, long):
    dataframe = file_parser.read_date_range_tick_file(ticker, start_date, end_date)

    if dataframe == None:
        return
    
    pnl_list = []
    cumulative_pnl = []
    
    for data in dataframe.values():
        data["Short MA"] = np.NAN
        data["Long MA"] = np.NAN

        short_list = [np.NAN]*short
        long_list = [np.NAN]*long

        position = 0
        buying_price = 0.0
        selling_price = 0.0

        for i in range(len(data)):
            short_ma, long_ma = np.NAN, np.NAN
            price = data["Price"][i]

            # Updating moving average list
            del short_list[0]
            short_list.append(price)
            del long_list[0]
            long_list.append(price)

            if i-1 >= short:
                short_ma = np.mean(short_list)
                data.at[i, "Short MA"] = short_ma

            if i-1 >= long:
                long_ma = np.mean(long_list)
                data.at[i, "Long MA"] = long_ma

                if short_ma > long_ma and data["Short MA"][i-1] < data["Long MA"][i-1]:
                    buying_price = data["Price"][i]

                    if position == 0:
                        position += 1
                    else:
                        position += 2
                        pnl_list.append(round((selling_price-buying_price)*100/selling_price, 2))

                if short_ma < long_ma and data["Short MA"][i-1] > data["Long MA"][i-1] and position > 0:
                    selling_price = data["Price"][i]

                    if position == 0:
                        position -= 1
                    else:
                        position -= 2
                        pnl_list.append(round((selling_price-buying_price)*100/buying_price, 2))

        # Close at end of day
        if position > 0:
            selling_price = data["Price"][len(data)-1]
            pnl_list.append(round((selling_price-buying_price)*100/buying_price, 2))
        elif position < 0:
            buying_price = data["Price"][len(data)-1]
            pnl_list.append(round((selling_price-buying_price)*100/selling_price, 2))

        position = 0

    for i in pnl_list:
        if len(cumulative_pnl) == 0:
            cumulative_pnl.append(i)
        else:
            cumulative_pnl.append(cumulative_pnl[-1]+i)

    plt.plot(cumulative_pnl)
    plt.title("Cumulative P&L")
    plt.xlabel("Trades")
    plt.ylabel("Profit (%)")
    plt.show()

    return (pnl_list, cumulative_pnl)