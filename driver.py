import pandas as pd
import preprocesser as pr
from positions import Positions

pd.options.display.max_rows = 999
pd.options.display.max_columns = 999

if __name__ == '__main__':
    df_grouped = pr.group_stock()
    pr.process_group(df_grouped)
    # print(Positions._positions)
    print(Positions._positions['AAPL'])