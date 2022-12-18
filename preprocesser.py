import pandas as pd
import numpy as np
from positions import Positions

# Load stock price data
PATH = '/Users/jacobseol/Projects/Stock-Scraper/'
FILE = 'stock_data.csv'

def group_stock() -> object:
    df = pd.read_csv(PATH+FILE)
    return df.groupby('ticker')

def get_position(df) -> object:
    # Convert string to number before processing the numbers to smooth out closing price data to identify trends
    df['close'] = df['close'].apply(lambda x: x.replace(',', ''))
    df['close'] = pd.to_numeric(df['close'])

    # Initialize the `signals` DataFrame with the `signal` column
    signals = pd.DataFrame(index=df.index)
    signals['signal'] = 0.0

    short_window = 50
    long_window = 100

    """
    window specifies the window size
    min_periods specifies the minimum number of periods (data points in our case) needed to perform a rolling calculation
        result is a mean or NaN if the current window does not contain enough periods
    center = False specifies that the rolling calculation will be performed on the whole window instead of it being centered
        on the data point in the middle of the window
    """
    # Create simple moving average over the short window
    signals['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1, center=False).mean()

    # Create simple moving average over the long window
    signals['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1, center=False).mean()

    """
    When the short mavg > long mavg for a given period, it is a potential indication of a bullish market and a buy signal is generated (value of 1)
    When the long mavg > short mavg for a given period, it is a potential indication of a bearish market and a sell signal is generated (value of 0)
    """
    # Create signals
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)   

    """
    Generate trading orders:

    Calculates the diff between current and previous values of signal for every single in the dataframe.
    If signal goes from 0 to 1 -> it is an indication of a bullish market and position is set to 1 (buy)
    If signal goes from 1 to 0 -> it is an indication of a bearish market and position is set to -1 (sell)
    If signal does not change -> it is an indication that no trading order should be generated, this can occur when the short and long moving average
        move in the same direction
    """ 
    signals['positions'] = signals['signal'].diff()
    return signals

def process_group(df_grouped) -> None:
    for name, group in df_grouped:
        Positions._positions[name] = get_position(group)

if __name__ == '__main__':
    group_stock()