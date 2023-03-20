import pandas as pd
from make_timeline import make_multi_timeline
import sys
import os

from make_js import make_js


def if_day_in_index(dt, df_res):
    for year in set(df_res.index.year):
        month_list = set(df_res.loc[str(year)].index.month)
        for month in month_list:
            day_list = set(df_res.loc[f'{year}-{month}'].index.day)
            for day in day_list:
                today = f'{year}-{month:02d}-{day:02d}'
                if dt.strftime("%Y-%m-%d") == today:
                    return True
    else:
        return False

# outputter = make_js("test_name")


dfs_trend = []
dfs_res = []
accounts = []

for f in os.listdir("./"):
    if f.startswith("trend_diff_") and f.endswith(".csv"):
        dfs_trend.append(pd.read_csv("result_cut_dif.csv",
                                     index_col="time", parse_dates=True))
        accounts.append(f[len("trend_diff_"):-1*len(".csv")])
    if f.startswith("res_diff_") and f.endswith(".csv"):
        dfs_res.append(pd.read_csv("result_cut_dif.csv",
                                   index_col="time", parse_dates=True))

# df_flw_1min = pd.read_csv("result_cut_dif.csv",
#                           index_col="time", parse_dates=True)
# df_flw_1min.sort_index(inplace=True)
# def make_multi_timeline(
#     dfs, figname,
#     y_label=None,
#     y_labels=None
# ):
make_multi_timeline(dfs_trend, "トレンドまとめ",
                    y_label="フォロワー数トレンド", y_labels=accounts)
make_multi_timeline(dfs_trend, "残差まとめ", y_label="フォロワー数残差", y_labels=accounts)
