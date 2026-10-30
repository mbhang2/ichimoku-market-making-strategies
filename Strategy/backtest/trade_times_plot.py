import plotly.graph_objects as go
import pandas as pd

def plot_trade_entries_exits(trade_df):
    """Plots the entry and exit timestamps for each trade in the dataframe by price as a stepwise function.

    x-axis: Time (%H:%M)
    y-axis: Price ($)

    Args:
        trade_df (pd.DataFrame): DataFrame with columns "Entry timestamp", "Exit timestamp", "Buying price", "Selling price".
    """
    
    sorted_trade_df = trade_df.sort_values(by="Entry timestamp")

    fig = go.Figure()

    for index, trade in sorted_trade_df.iterrows():
        entry_time = trade["Entry timestamp"]
        exit_time = trade["Exit timestamp"]
        buying_price = trade["Buying price"]
        selling_price = trade["Selling price"]

        # Entry and exit points connected by a stepwise line
        fig.add_trace(go.Scatter(x=[entry_time, exit_time], 
                                 y=[buying_price, selling_price], 
                                 mode='lines+markers', 
                                 name=f"Trade {index}"
                                 )
                     )

        # Different markers for open and close
        fig.add_trace(go.Scatter(x=[entry_time], 
                                 y=[buying_price], 
                                 mode='markers', 
                                 marker=dict(symbol='circle', 
                                             size=10, 
                                             color='green', 
                                             line=dict(color='black', width=1)), 
                                 name='Trade Open')
                     )
        fig.add_trace(go.Scatter(x=[exit_time], 
                                 y=[selling_price], 
                                 mode='markers', 
                                 marker=dict(symbol='x', 
                                             size=8, 
                                             color='red'), 
                                 name='Trade Close')
                     )

    fig.update_layout(
        title='Trade Entry and Exit Times',
        xaxis_title='Time',
        yaxis_title='Price',
        xaxis=dict(tickformat='%H:%M'),
    )

    fig.show()