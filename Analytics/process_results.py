# process orders and results
import os, os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn as sns
import re
import argparse
import glob


def plot_results(id: str, ichi: str, agg: str, spread: str):
    pnl_pattern = fr'BACK_*_{id}_*_pnl.csv'
    pnl_files = glob.glob(os.path.join(path, pnl_pattern))
    
    fil_pattern = fr'BACK_*_{id}_*_fill.csv'
    fil_files = glob.glob(os.path.join(path, fil_pattern))

    if not fil_files or not pnl_files:
        print("Missing files, check directory")
        return

    pnl = pd.read_csv(pnl_files[0], header=0)
    pnl = pnl[~pnl['Time'].str.contains('05:00:00')]
    pnl['Time'] = pd.to_datetime(pnl['Time'], dayfirst=True)

    fil_cols = ['TradeTime',  
    			'Symbol',
    			'Quantity',
    			'Price',
    			'ExecutionCost',
    			'LiquidityAction',
    			'MarketCenter',
    			'OrderID']

    fil = pd.read_csv(fil_files[0], header=0, usecols=fil_cols)
    fil['TradeTime'] = pd.to_datetime(fil['TradeTime'], dayfirst=0)
	
    sns.set_palette("viridis", desat=.6)
    sns.set_context(rc={"figure.figure": (12, 18)})

    fig = plt.figure(constrained_layout=True)
    gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 1], width_ratios=[7, 2.4])

    fig.patch.set_facecolor('white')  # Set the outer color to white

	# period calculations
    start = fil['TradeTime'].min().strftime('%m/%d/%Y')
    end = fil['TradeTime'].max().strftime('%m/%d/%Y')

	# max drawdown
    rolling_max = pnl['Cumulative PnL'].cummax()
    drawdowns = pnl['Cumulative PnL'] / (rolling_max - 1.0)
    max_drawdowns = drawdowns.max() 

	# sharpe ratio (current 10 year treasury yield is 3.95%)
    rf_per_period = (1 + 0.0395)**(1/252) - 1  # Assuming 252 trading days in a year
    excess_returns = pnl['Cumulative PnL'] - rf_per_period
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)

    table_data = [
	    [f'{id}'],
	    [f'{ichi}'],
	    [f'{agg}'],
	    [f'{spread}'],
	    [f'{sharpe_ratio:.5f}'],
	    [f'{max_drawdowns:.5f}']
	]

    row_labels = ['ID:', 
	              'Ichimoku Input:', 
	              'Aggression:', 
	              'Spread Threshold:', 
	              'Sharpe Ratio:', 
	              'Max Drawdown:']

	# Subplot 1 (ax1)
    ax1 = plt.subplot(gs[0, 0], ylabel='Trade Price')
    fil["Price"].plot(ax=ax1, color=sns.color_palette()[2], drawstyle='steps-post')
    ax1.set_xticks([])
    ax1.yaxis.set_label_coords(-0.3, 0.8)
    ax1.yaxis.label.set_rotation(0)
    ax1.yaxis.label.set_weight('bold')

	# Subplot 2 (ax2)
    ax2 = plt.subplot(gs[1, 0], ylabel='Cumulative PnL')
    pnl['Cumulative PnL'].plot(ax=ax2, color=sns.color_palette()[5])
    ax2.axhline(y=0, color=sns.color_palette('magma')[1], linestyle='--', linewidth=0.5)
    ax2.set_xticks([])
    ax2.yaxis.set_label_coords(-0.3, 0.8)
    ax2.yaxis.label.set_rotation(0)
    ax2.yaxis.label.set_weight('bold')

    # Subplot 3 (ax3)
    ax3 = plt.subplot(gs[2, 0], xlabel='Time', ylabel='Buy vs Sell')
    sell_data = fil[fil['LiquidityAction'] == 'ADDED']
    buy_data = fil[fil['LiquidityAction'] == 'REMOVED']
    ax3.plot(sell_data['TradeTime'], sell_data['Price'], color=sns.color_palette('seismic')[5], label='Sell')
    ax3.plot(buy_data['TradeTime'], buy_data['Price'], color='green', label='Buy')
    ax3.xaxis.label.set_weight('bold')
    ax3.tick_params(axis='x', rotation=45)
    ax3.yaxis.set_label_coords(-0.3, 0.8)
    ax3.yaxis.label.set_rotation(0)
    ax3.yaxis.label.set_weight('bold')
    ax3.legend(loc='upper right')

    ax0 = plt.subplot(gs[0, 1])
    table = ax0.table(cellText=table_data, rowLabels=row_labels, 
                        rowLoc='right',
                        loc='right', 
                        cellLoc='right',
                        colLoc='bottom', 
                        edges='vertical')
    table.set_snap(False)
    ax0.axis('off')

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.set_snap(True)

    # Title for the entire figure
    fig.suptitle(f'{pnl.iloc[0,0]}, Period: {start}-{end}', fontsize=16, fontweight='bold')

    image_dir = os.path.expanduser('~/Documents/group_02_project/Images/')
    os.makedirs(image_dir, exist_ok=True)

    filename = f'{pnl.iloc[0, 0]}_{id}'
    image_path = os.path.join(image_dir, f'{filename}.png')
    plt.savefig(image_path, dpi=500)

if __name__ == "__main__":
    path = './csv_files'

    parser = argparse.ArgumentParser(description="Process Order and PnL data with the given identifier.")
    parser.add_argument("identifier", type=str, help="Unique identifier for the file pattern.")
    parser.add_argument("ichimoku_input", type=str, help="Ichimoku Input.")
    parser.add_argument("aggression", type=str, help="Aggression.")
    parser.add_argument("spread_threshold", type=str, help="Spread Threshold.")

    args = parser.parse_args()

    plot_results(args.identifier, args.ichimoku_input, args.aggression, args.spread_threshold)