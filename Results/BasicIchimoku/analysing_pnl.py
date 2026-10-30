import pandas as pd
import plotly.express as px

def plot_multiple_dfs(*dataframes, pnl_column='Cumulative PnL', time_column='Time', title='Cumulative PnL over Time'):
    """
    Plots multiple dataframes on the same Plotly line plot.

    :param dataframes: Variable number of dataframes to plot.
    :param pnl_column: Name of the column containing PnL values.
    :param time_column: Name of the column containing time values.
    :param title: Title of the plot.
    """
    # Concatenate all dataframes with an additional 'Source' column to identify them
    all_data = pd.concat([df.assign(Source=f"DF{i+1}") for i, df in enumerate(dataframes)], ignore_index=True)

    # Ensure that time_column is in datetime format
    all_data[time_column] = pd.to_datetime(all_data[time_column])

    # Create the plot
    fig = px.line(all_data, x=time_column, y=pnl_column, color='Source', title=title)

    # Display the plot
    fig.show()


main_dir = "/home/ashitabh/Documents/ss/bt/backtesting-results/csv_files/"

df_1_path = "BACK_BasicIchimoku_2023-12-15_082137_start_01-03-2023_end_01-03-2023_pnl.csv"
df_2_path = "BACK_BasicIchimoku_2023-12-15_082554_start_01-03-2023_end_01-03-2023_pnl.csv"

df_1 = pd.read_csv(main_dir + df_1_path)
df_2 = pd.read_csv(main_dir + df_2_path)

# Example Usage
# Assuming df1, df2, ... dfn are your dataframes with 'Time' and 'Cumulative PnL' columns
plot_multiple_dfs(df_1, pnl_column='Cumulative PnL', time_column='Time')
