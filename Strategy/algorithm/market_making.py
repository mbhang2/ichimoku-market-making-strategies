import numpy as np
import os
import pandas as pd
import sys

dir = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(dir))

from Strategy.utility.order import Order, Limit, Market, Stop


"""
Returns list of orders to be made
"""
# def directional_market_making_order(order_no, timestamp, side, bid_price, ask_price, size, **kwargs):
#     orders = None

#     # parameters
#     num_stop_loss = kwargs.get("num_stop_loss", 0)
#     stop_loss_tick = kwargs.get("stop_loss_tick", 0)
#     offset = kwargs.get("offset", 3)
#     flag = kwargs.get("flag", "GTD")

#     # Send orders
#     if num_stop_loss == 0:
#         if side == "buy":
#             orders = [Limit(order_no, timestamp, "limit", "buy", bid_price, size, None, np.NAN, None, flag), Limit(order_no, timestamp+pd.Timedelta(microseconds=0.001), "limit", "sell", ask_price + 0.01*offset, -size, None, np.NAN, None, flag)]
#         else:
#             orders = [Limit(order_no, timestamp+pd.Timedelta(microseconds=0.001), "limit", "buy", bid_price - 0.01*offset, size, None, np.NAN, None, flag), Limit(order_no, timestamp, "limit", "sell", ask_price, -size,  None, np.NAN, None, flag)]

#     elif num_stop_loss == 1:
#         if side == "buy":
#             sell_limit = Limit(order_no, timestamp+pd.Timedelta(microseconds=0.001), "limit", "sell", ask_price + 0.01*offset, -size, None, np.NAN, None, flag)
#             open_stop_loss = Stop(order_no, timestamp+pd.Timedelta(microseconds=0.002), "stop", "sell", bid_price-0.01*stop_loss_tick, -size, None, np.NAN, sell_limit, flag)
#             sell_limit.competing_order = open_stop_loss
#             orders = [Limit(order_no, timestamp, "limit", "buy", bid_price, size, None, np.NAN, None, flag), sell_limit, open_stop_loss]
#         else:
#             buy_limit = Limit(order_no, timestamp+pd.Timedelta(microseconds=0.001), "limit", "buy", bid_price - 0.01*offset, size, None, np.NAN, None, flag)
#             open_stop_loss = Stop(order_no, timestamp+pd.Timedelta(microseconds=0.002), "stop", "buy", ask_price-0.01*stop_loss_tick, size, None, np.NAN, buy_limit, flag)
#             buy_limit.competing_order = open_stop_loss
#             orders = [buy_limit, Limit(order_no, timestamp, "limit", "sell", ask_price, -size,  None, np.NAN, None, flag), open_stop_loss]

#     elif num_stop_loss == 2:
#         if side == "buy":
#             buy_limit = Limit(order_no, timestamp, "limit", "buy", bid_price, size, None, np.NAN, None, flag)
#             sell_limit = Limit(order_no, timestamp+pd.Timedelta(microseconds=0.001), "limit", "sell", ask_price + 0.01*offset, -size, None, np.NAN, None, flag)
#             open_stop_loss = Stop(order_no, timestamp+pd.Timedelta(microseconds=0.002), "stop", "sell", bid_price-0.01*stop_loss_tick, -size, None, np.NAN, sell_limit, flag)
#             close_stop_loss = Stop(order_no, timestamp+pd.Timedelta(microseconds=0.003), "stop", "buy", ask_price+0.01*(offset+stop_loss_tick), size, None, np.NAN, buy_limit, flag)
#             sell_limit.competing_order = open_stop_loss
#             buy_limit.competing_order = close_stop_loss
#             orders = [buy_limit, sell_limit, open_stop_loss, close_stop_loss]
#         else:
#             buy_limit = Limit(order_no, timestamp+pd.Timedelta(microseconds=0.001), "limit", "buy", bid_price - 0.01*offset, size, None, np.NAN,None, flag)
#             sell_limit = Limit(order_no, timestamp, "limit", "sell", ask_price, -size,  None, np.NAN, None, flag)
#             open_stop_loss = Stop(order_no, timestamp+pd.Timedelta(microseconds=0.002), "stop", "buy", ask_price-0.01*stop_loss_tick, size, None, np.NAN, buy_limit, flag)
#             close_stop_loss = Stop(order_no, timestamp+pd.Timedelta(microseconds=0.003), "stop", "sell", bid_price-0.01*(offset+stop_loss_tick), -size, None, np.NAN, sell_limit, flag)
#             buy_limit.competing_order=open_stop_loss
#             sell_limit.competing_order=close_stop_loss
#             orders = [buy_limit, sell_limit, open_stop_loss, close_stop_loss]

#     return orders


def directional_market_making_order(order_group, timestamp, side, bid_price, ask_price, size, **kwargs):
    orders = None

    # parameters
    num_stop_loss = kwargs.get("num_stop_loss", 0)
    stop_loss_tick = kwargs.get("stop_loss_tick", 0)
    offset = kwargs.get("offset", 3)
    flag = kwargs.get("flag", "GTD")

    # Send orders
    if num_stop_loss == 0:
        if side == "buy":
            orders = [Limit(order_group, timestamp, "limit", "buy", bid_price, size, None, np.NAN, None, flag), Limit(order_group, timestamp+pd.Timedelta(microseconds=0.001), "limit", "sell", ask_price + 0.01*offset, -size, None, np.NAN, None, flag)]
        else:
            orders = [Limit(order_group, timestamp, "limit", "sell", ask_price, -size,  None, np.NAN, None, flag), Limit(order_group, timestamp+pd.Timedelta(microseconds=0.001), "limit", "buy", bid_price - 0.01*offset, size, None, np.NAN, None, flag)]

    return orders

