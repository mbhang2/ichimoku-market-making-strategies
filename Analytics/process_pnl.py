import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
import argparse
import glob

def process_pnl(id: str): 
    pattern = fr'BACK_*_{id}_*_pnl.csv'

    matching_files = glob.glob(os.path.join(path, pattern))

    if not matching_files:
        print(f"No files found for pattern: {pattern}")
        return

    file_name = matching_files[0]

    pnl = pd.read_csv(file_name, header=0)

    # Time Series Plot
    fig_time_series = go.Figure()
    fig_time_series.add_trace(go.Scatter(x=pnl['Time'], y=pnl['Cumulative PnL'], mode='lines', name='Cumulative PnL'))
    fig_time_series.update_layout(title='Cumulative PnL Over Time',
                                  xaxis=dict(title='Time'),
                                  yaxis=dict(title='Cumulative PnL'),
                                  template='plotly_dark')

    fig_time_series.write_image(f'time_series_{id}.png')

    # Drawdown Plot
    fig_drawdown = go.Figure()
    fig_drawdown.add_trace(go.Scatter(x=pnl['Time'], y=pnl['Cumulative PnL'].cummax() - pnl['Cumulative PnL'],
                                      fill='tozeroy', mode='none', name='Drawdown'))
    max_drawdown_idx = pnl['Cumulative PnL'].idxmin()
    max_drawdown_value = pnl['Cumulative PnL'].min()
    fig_drawdown.add_annotation(go.layout.Annotation(x=pnl['Time'][max_drawdown_idx], y=max_drawdown_value,
                                                     text=f'Max Drawdown: {max_drawdown_value:.2f}',
                                                     showarrow=True, arrowhead=1, arrowcolor='red'))
    fig_drawdown.update_layout(title='Drawdown Over Time',
                               xaxis=dict(title='Time'),
                               yaxis=dict(title='Drawdown'),
                               template='plotly_dark')

    fig_drawdown.write_image(f'drawdown_{id}.png')

if __name__ == "__main__":
    # Set the path to the directory containing the CSV files
    path = './'

    parser = argparse.ArgumentParser(description="Process PnL data with given identifier.")
    parser.add_argument("identifier", type=str, help="Unique identifier for the file pattern.")

    args = parser.parse_args()

    process_pnl(args.identifier)