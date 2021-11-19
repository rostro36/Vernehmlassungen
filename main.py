import pandas as pd
from download import get_page
from process import process_year
import time
from variables import YEAR_BASE, HISTORY_BASE

if __name__ == "__main__":
    df_dict = dict()
    for retry in range(3):
        for year in range(1992, 2022):
            print(year)
            if year not in df_dict:
                html = get_page(YEAR_BASE+str(year))
                processed = process_year(html)
                if processed is not None:
                    df_dict[year] = processed
                    time.sleep(2)
    dfs = []
    for year in df_dict:
        dfs.append(df_dict[year])
    df = pd.concat(dfs)
    df.to_csv('second_data.csv')
