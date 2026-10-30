import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def percent_to_decimal(column):
    return float(column.rstrip('%'))


def scatter_plot(file, variable, column):
    df = pd.read_table(file, sep='\t', converters={"pnl":percent_to_decimal, "winrate":percent_to_decimal, "avg_profit":percent_to_decimal, "avg_loss":percent_to_decimal})

    variable_category = df[variable].unique()

    for i in variable_category:
        col = list(df[df[variable].isin([i])][column])
        plt.scatter([i]*len(col), col, label=f"{variable}: {i}")

    plt.legend()
    plt.show()

def two_col_scatter(file, variable, x, y):
    df = pd.read_table(file, sep='\t', converters={"pnl":percent_to_decimal, "winrate":percent_to_decimal, "avg_profit":percent_to_decimal, "avg_loss":percent_to_decimal})

    variable_category = df[variable].unique()

    for i in variable_category:
        col1 = list(df[df[variable].isin([i])][x])
        col2 = list(df[df[variable].isin([i])][y])
        plt.scatter(col1, col2, label=f"{variable}: {i}")
        plt.xlabel(x)
        plt.ylabel(y)

    plt.legend()
    plt.show()

def two_col_multi_scatter(file, v1, v2, v3, v4, x, y):
    df = pd.read_table(file, sep='\t', converters={"pnl":percent_to_decimal, "winrate":percent_to_decimal, "avg_profit":percent_to_decimal, "avg_loss":percent_to_decimal})

    l = [v1,v2,v3,v4]
    fig, axis = plt.subplots(2, 2) 

    for index in range(4):
        v = df[l[index]].unique()

        for i in v:
            col1 = list(df[df[l[index]].isin([i])][x])
            col2 = list(df[df[l[index]].isin([i])][y])
            
            axis[int(index/2), index%2].scatter(col1, col2, label=f"{l[index]}: {i}")
            axis[int(index/2), index%2].set_title(l[index])
            axis[int(index/2), index%2].set_xlabel(x)
            axis[int(index/2), index%2].set_ylabel(y)
            axis[int(index/2), index%2].legend()

    fig.tight_layout()
    plt.legend()
    plt.show()


two_col_multi_scatter("Strategy/backtest/backtest_result/QQQ_ichimoku_length_vs_strategy_vs_offset_vs_position_size.txt", "ichimoku_length", "ichimoku_strategy", "offset", "position", "winrate", "pnl")