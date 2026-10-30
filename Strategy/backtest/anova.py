import numpy as np
import pandas as pd
import researchpy as rp
import statsmodels.api as sm
from statsmodels.formula.api import ols
from tabulate import tabulate


pd.set_option('display.max_rows', None)


def percent_to_decimal(column):
    return float(column.rstrip('%'))

def anova(file):
    df = pd.read_table(file, sep='\t', converters={"pnl":percent_to_decimal, "winrate":percent_to_decimal, "avg_profit":percent_to_decimal, "avg_loss":percent_to_decimal})

    # perform Four-way ANOVA for P&L
    model = ols("""pnl ~ C(ichimoku_length) + C(ichimoku_strategy) + C(offset) + C(position) +
                C(ichimoku_length):C(ichimoku_strategy) + C(ichimoku_length):C(offset) + C(ichimoku_length):C(position) +
                C(ichimoku_strategy):C(offset) + C(ichimoku_strategy):C(position) + C(offset):C(position) +
                C(ichimoku_length):C(ichimoku_strategy):C(offset) + C(ichimoku_length):C(ichimoku_strategy):C(position) +
                C(ichimoku_length):C(offset):C(position) + C(ichimoku_strategy):C(offset):C(position)""", data=df).fit()

    anova_table = sm.stats.anova_lm(model, test="F", typ=2)

    print("\nP&L")
    print(tabulate(anova_table, headers = 'keys', tablefmt = 'psql'))

    # perform Four-way ANOVA for Win Rate
    model = ols("""winrate ~ C(ichimoku_length) + C(ichimoku_strategy) + C(offset) + C(position) +
                C(ichimoku_length):C(ichimoku_strategy) + C(ichimoku_length):C(offset) + C(ichimoku_length):C(position) +
                C(ichimoku_strategy):C(offset) + C(ichimoku_strategy):C(position) + C(offset):C(position) +
                C(ichimoku_length):C(ichimoku_strategy):C(offset) + C(ichimoku_length):C(ichimoku_strategy):C(position) +
                C(ichimoku_length):C(offset):C(position) + C(ichimoku_strategy):C(offset):C(position)""", data=df).fit()

    anova_table = sm.stats.anova_lm(model, test="F", typ=2)

    print("\nWin Rate")
    print(tabulate(anova_table, headers = 'keys', tablefmt = 'psql'))

anova("Strategy/backtest/backtest_result/QQQ_ichimoku_length_vs_strategy_vs_offset_vs_position_size.txt")
