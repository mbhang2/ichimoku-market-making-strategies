import numpy as np
import os
import pandas as pd
import sys

dir = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(dir))

from Strategy.algorithm import ichimoku, market_making
from Strategy.utility.order import Order, Limit, Market


def run_backtest_no_stop_loss(df, **kwargs):
    """
    Accepts output from candlestick function as a input dataframe
    """
    # Miscellaneous parameters
    capital = kwargs.get("capital", 10**6)
    position_size_per_trade = kwargs.get("position_size_per_trade", 5)

    # Parse algorithmic and marketmaking methods
    algorithm = kwargs.get("algorithm", "ICHIMOKU").upper()

    if algorithm == "ICHIMOKU":
        short = kwargs.get("short", 9)
        mid = kwargs.get("mid", 26)
        long = kwargs.get("long", 52)
        ichimoku_strategy = kwargs.get("ichimoku_strategy", 0)
        ichimoku.compute_ichimoku(df, 9, 26, 52)

    order_offset = kwargs.get("order_offset", 3)

    working_order_df = pd.DataFrame(columns=["Order group", "Order", "Status"])
    filled_order_df = pd.DataFrame(columns = ["Order group", "Order"])
    trade_df = pd.DataFrame(columns=["Order group", "Open Order", "Close Order", "P&L", "P&L percent", "Equity"])

    order_group = 0

    for row in range(len(df)):
        # update at the start of the day
        if row == 0 or df["Time"][row-1] < pd.Timestamp(df["Time"][row].date()):
            order_group = 0
            buying_power = capital
            last_entered_bar_number = -1
            working_order_df = pd.DataFrame(columns=["Order group", "Order", "Status"])
            filled_order_df = pd.DataFrame(columns = ["Order group", "Order"])

        if row < short - 1:
            continue

        """ Manage ongoing order first """
        for index in range(len(working_order_df)):
            curr = working_order_df["Order"][index]

            if curr.check_fill_availability(df["Bid price"][row], df["Bid size"][row], df["Ask price"][row], df["Ask size"][row]):
                # Fill the order
                curr.fill_order(df["Time"][row], df["Ask price"][row] if curr.side == "buy" else df["Bid price"][row])

                # Update
                buying_power += curr.size * curr.filled_price
                filled_order_df.loc[len(filled_order_df)] = [curr.order_no, curr]
                working_order_df.drop([index], inplace=True)

        working_order_df.reset_index(drop=True, inplace=True)


        """ Search if trade condition met """
        trade_signal = ichimoku.trade_signal(df, row, ichimoku_strategy, short, mid, long)

        if df["Bar number"][row] > last_entered_bar_number and trade_signal == 1 and buying_power/capital >= 0.01 * position_size_per_trade: # Buy signal
            [order_in_favor, order_against] = market_making.directional_market_making_order(order_group, df["Time"][row], "buy", df["Bid price"][row], df["Ask price"][row], int(capital*0.01*position_size_per_trade/df["Close"][row]), offset=order_offset)
            
            working_order_df.loc[len(working_order_df)] = [order_group, order_in_favor, "working"]      # Record buy order
            working_order_df.loc[len(working_order_df)] = [order_group, order_against, "working"]       # Record sell order

            last_entered_bar_number = df["Bar number"][row]
            order_group += 1
            buying_power -= order_in_favor.size * (order_in_favor.price - order_against.price)

        elif df["Bar number"][row] > last_entered_bar_number and trade_signal == -1 and buying_power/capital >= 0.01 * position_size_per_trade: # Sell signal
            [order_in_favor, order_against] = market_making.directional_market_making_order(order_group, df["Time"][row], "sell", df["Bid price"][row], df["Ask price"][row], int(capital*0.01*position_size_per_trade/df["Close"][row]), offset=order_offset)
            working_order_df.loc[len(working_order_df)] = [order_group, order_in_favor, "working"]      # Record sell order
            working_order_df.loc[len(working_order_df)] = [order_group, order_against, "working"]       # Record buy order

            last_entered_bar_number = df["Bar number"][row]
            order_group += 1
            buying_power -= order_in_favor.size * (order_against.price - order_in_favor.price)

        
        """ Close any unfilled order and record in trade dataframe """
        if row == len(df) - 1 or df["Time"][row] < pd.Timestamp(df["Time"][row+1].date()):
            for i in range(order_group):
                unfilled_df = working_order_df.loc[working_order_df["Order group"] == i]
                filled_df = filled_order_df.loc[filled_order_df["Order group"] == i]
                filled_df.reset_index(drop=True, inplace=True)

                if len(unfilled_df) == 1:   # Fill the working close order
                    index = unfilled_df.index.values[0]
                    curr = working_order_df["Order"][index]
                    
                    curr.fill_order(df["Time"][row-1], df["Ask price"][row-1] if curr.side == "buy" else df["Bid price"][row-1])
                    filled_order_df.loc[len(filled_order_df)] = [curr.order_no, curr]          
                    working_order_df.drop(index, inplace=True)

                if len(unfilled_df) == 2:   # Cancel both orders
                    index = unfilled_df.index.values
                    working_order_df["Order"][index[0]].cancel_order()
                    working_order_df["Order"][index[1]].cancel_order()
                    
                    working_order_df.drop(index, inplace=True)

                if len(filled_df) == 2:     # Record in trade df
                    open_order = filled_df["Order"][0] if filled_df["Order"][0].filled_timestamp < filled_df["Order"][1].filled_timestamp else filled_df["Order"][1]
                    close_order = filled_df["Order"][0] if filled_df["Order"][0].filled_timestamp > filled_df["Order"][1].filled_timestamp else filled_df["Order"][1]
                    buy_order = open_order if open_order.side == "buy" else close_order
                    sell_order = open_order if open_order.side == "sell" else close_order

                    pnl = buy_order.size * (sell_order.filled_price - buy_order.filled_price)
                    trade_df.loc[len(trade_df)] = [i, open_order, close_order, pnl, pnl*100/capital, capital+pnl]
                    capital += pnl

    return trade_df
