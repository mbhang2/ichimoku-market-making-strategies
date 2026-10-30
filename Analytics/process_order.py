import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
import argparse
import glob

def process_order(id: str):
    pattern = fr'BACK_*_{id}_*_order.csv'

    matching_files = glob.glob(os.path.join(path, pattern))

    if not matching_files:
        print(f"No files found for pattern: {pattern}")
        return

    file_name = matching_files[0]

    ord = pd.read_csv(file_name, header=0)

    ord['EntryTime'] = pd.to_datetime(ord['EntryTime'])

    # Figure 1: Buy, Sell, and Cancelled Orders Over Time
    fig_orders_over_time = go.Figure()

    # Separate buy, sell, and cancelled orders
    for side, color in [('BUY', 'blue'), ('SELL', 'red'), ('CANCELLED', 'gray')]:
        orders = ord[(ord['Side'] == side) & (ord['State'] != 'CANCELLED')] if side != 'CANCELLED' else ord[ord['State'] == 'CANCELLED']
        fig_orders_over_time.add_trace(go.Scatter(x=orders['EntryTime'], y=orders['Quantity'],
                                                  mode='markers' if side == 'CANCELLED' else 'lines',
                                                  name=f'{side} Orders', marker=dict(color=color)))

    # Update layout for Figure 1
    fig_orders_over_time.update_layout(title='Buy, Sell, and Cancelled Orders Over Time',
                                       xaxis=dict(title='Time'),
                                       yaxis=dict(title='Order Quantity', tickmode='linear', dtick=15),
                                       template='plotly_dark')
    fig_orders_over_time.write_image(f'orders_over_time_{id}.png')

    # Figure 2: Execution Prices Over Time
    fig_execution_prices = go.Figure()

    # Filter out cancelled orders
    filtered_ord = ord[ord['State'] != 'CANCELLED']
    fig_execution_prices.add_trace(go.Scatter(x=filtered_ord['EntryTime'], y=filtered_ord['Price'],
                                              mode='markers', name='Execution Prices', marker=dict(color='green')))

    # Update layout for Figure 2
    fig_execution_prices.update_layout(title='Execution Prices Over Time',
                                       xaxis=dict(title='Time'),
                                       yaxis=dict(title='Execution Price'),
                                       template='plotly_dark')
    fig_execution_prices.write_image(f'execution_prices_{id}.png')

    # Figure 3: Execution Prices Over Time with Colors for Buy and Sell
    fig_execution_prices_color = go.Figure()

    for side, color in [('BUY', 'blue'), ('SELL', 'red')]:
        trace = go.Scatter(x=filtered_ord[filtered_ord['Side'] == side]['EntryTime'],
                           y=filtered_ord[filtered_ord['Side'] == side]['Price'],
                           mode='lines', name=f'{side} Orders', marker=dict(color=color))
        fig_execution_prices_color.add_trace(trace)

    # Update layout for Figure 3
    fig_execution_prices_color.update_layout(title='Execution Prices Over Time (Buy in Blue, Sell in Red)',
                                            xaxis=dict(title='Time'),
                                            yaxis=dict(title='Execution Price'),
                                            template='plotly_dark')
    
    fig_execution_prices_color.write_image(f'execution_prices_over_time_side_{id}.png')

    # Figure 4: Cumulative Execution Cost Over Time
    fig_cumulative_execution_cost = go.Figure()

    # Filter out cancelled orders
    filtered_ord = ord[ord['State'] != 'CANCELLED']

    filtered_ord['CumulativeExecutionCost'] = filtered_ord['ExecutionCost'].cumsum()

    fig_cumulative_execution_cost.add_trace(go.Scatter(x=filtered_ord['EntryTime'],
                                                       y=filtered_ord['CumulativeExecutionCost'],
                                                       mode='lines', name='Cumulative Execution Cost', line=dict(color='purple')))

    total_cost = filtered_ord['CumulativeExecutionCost'].iloc[-1]

    fig_cumulative_execution_cost.add_annotation(x=filtered_ord['EntryTime'].iloc[-1],
                                                  y=total_cost,
                                                  text=f'Total Cost: ${total_cost:.2f}',
                                                  showarrow=False,
                                                  font=dict(color='black'),
                                                  bgcolor='white',
                                                  bordercolor='black',
                                                  borderwidth=2,
                                                  xref='x',
                                                  yref='y')

    # Update layout for Figure 4
    fig_cumulative_execution_cost.update_layout(title='Cumulative Execution Cost Over Time',
                                                xaxis=dict(title='Time'),
                                                yaxis=dict(title='Cumulative Execution Cost'),
                                                template='plotly_dark')
    
    fig_cumulative_execution_cost.write_image(f'cumulative_execution_cost_{id}.png')

if __name__ == "__main__":
    # Set the path to the directory containing the CSV files
    path = './'

    parser = argparse.ArgumentParser(description="Process Order data with given identifier.")
    parser.add_argument("identifier", type=str, help="Unique identifier for the file pattern.")

    args = parser.parse_args()

    process_order(args.identifier)
