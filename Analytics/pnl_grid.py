import argparse
import glob
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_and_process_data(id, path):
    pnl_pattern = fr'BACK_*_{id}_*_pnl.csv'
    pnl_files = glob.glob(os.path.join(path, pnl_pattern))
    if not pnl_files:
        print(f"No PnL files found for ID: {id}")
        return None, None
    pnl = pd.read_csv(pnl_files[0], header=0)
    pnl = pnl[~pnl['Time'].str.contains('05:00:00')]
    pnl['Time'] = pd.to_datetime(pnl['Time'])
    pnl['Cumulative PnL (%)'] = (pnl['Cumulative PnL'] / 1000000) * 100
    strategy_name = pnl.iloc[0, 0]
    return pnl, strategy_name

# def normalize_pnl(pnl):
#     min_pnl = pnl['Cumulative PnL'].min()
#     max_pnl = pnl['Cumulative PnL'].max()
#     pnl['Normalized PnL'] = (pnl['Cumulative PnL'] - min_pnl) / (max_pnl - min_pnl)
#     return pnl

def calculate_metrics(pnl):
    # max drawdown
    # rolling_max = pnl['Cumulative PnL'].cummax()
    # drawdowns = pnl['Cumulative PnL'] / (rolling_max - 1.0)
    # max_drawdown = drawdowns.min() 

    rolling_max = pnl['Cumulative PnL'].cummax()
    drawdowns = rolling_max - pnl['Cumulative PnL']
    max_drawdown = -drawdowns.max()
    max_drawdown = (max_drawdown / 1000000) * 100

	# sharpe ratio (current 10 year treasury yield is 3.95%)
    rf_per_period = (1 + 0.0395)**(1/252) - 1  # Assuming 252 trading days in a year
    excess_returns = pnl['Cumulative PnL'] - rf_per_period
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)

    return f'{sharpe_ratio:.5f}', f'{max_drawdown:.5f}'

def plot_pnl_grid(identifiers, path, annotations):
    sns.set(style="whitegrid")
    sns.set_palette("viridis", desat=.6)
    num_plots = len(identifiers)
    cols = 2
    rows = num_plots // cols + num_plots % cols
    fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(10, 5 * rows), sharex=True)
    axes = axes.flatten()

    # Determine the common y-axis range
    y_min, y_max = float('inf'), float('-inf')
    for id in identifiers:
        pnl, _ = load_and_process_data(id, path)
        if pnl is not None:
            y_min = min(y_min, pnl['Cumulative PnL (%)'].min())
            y_max = max(y_max, pnl['Cumulative PnL (%)'].max())

    for ax, id, annotation in zip(axes, identifiers, annotations):
        pnl, strategy_name = load_and_process_data(id, path)
        if pnl is not None:
            sns.lineplot(x='Time', y='Cumulative PnL (%)', data=pnl, ax=ax, linewidth=2)
            ax.set_title(f"{id}", ha='center', weight='bold')
            ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)
            ax.tick_params(axis='x', labelrotation=45)
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_ylim(y_min, y_max)  # Set the common y-axis range
            sharpe_ratio, max_drawdown = calculate_metrics(pnl)
            annotation += (f'\\nSharpe Ratio: {sharpe_ratio}\\nMax Drawdown: {max_drawdown}')
            formatted_annotation = annotation.replace('\\n', '\n')
            
            ax.text(0.05, 0.30, formatted_annotation, transform=ax.transAxes, 
                    va='top', ha='left', bbox=dict(boxstyle="round,pad=0.3", 
                    fc="white", ec="black", lw=1))

    fig.supxlabel('Time', ha='center', va='center', weight='bold', y=0.02)
    fig.supylabel('Cumulative PnL (%)', ha='center', va='center', rotation='vertical', weight='bold', x=0.02)
    plt.suptitle(f"{strategy_name} ({pnl['Time'].min().strftime('%m-%d-%Y')} - {pnl['Time'].max().strftime('%m-%d-%Y')})", 
                 fontsize=16, 
                 weight='bold',
                 y=1.00,
                 ha='center')
    
    plt.tight_layout()
    plt.savefig(f'../MVWAPCrypto/results/{strategy_name}_{id}.png', dpi=500)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot PnL scatter plots for multiple strategies.")
    parser.add_argument("identifiers", nargs='+', help="Unique identifiers for the strategies.")
    args = parser.parse_args()

    path = '../MVWAPCrypto/results/'

    annotations = []
    for id in args.identifiers:
        annotation = input(f"What are the notes for {id}? ")
        annotations.append(annotation)

    plot_pnl_grid(args.identifiers, path, annotations)