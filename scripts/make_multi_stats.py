import pandas as pd
from make_timeline import make_multi_timeline
import sys
import os
from datetime import datetime, timedelta

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
dfs_season = []

for f in os.listdir("./"):
    if f.endswith(".csv"):
        if f.startswith("trend_diff_"):
            dfs_trend.append(pd.read_csv(f, index_col="time", parse_dates=True, header=0, names=[
                             "time", f[len("trend_diff_"):-1*len(".csv")]]))
        if f.startswith("res_diff_"):
            dfs_res.append(pd.read_csv(f, index_col="time", parse_dates=True, header=0, names=[
                           "time", f[len("res_diff_"):-1*len(".csv")]]))
        if f.startswith("season_diff_"):
            dfs_season.append(pd.read_csv(f, index_col="time", parse_dates=True, header=0, names=[
                              "time", f[len("season_diff_"):-1*len(".csv")]]))

# pj_sekaiのみ過去データが多いので、マージグラフでその部分を大雑把に除く
dfs_trend_xmin = max([min(df.index) for df in dfs_trend])

dfs_trend = [df[df.index >= dfs_trend_xmin] for df in dfs_trend]

# seasonal, resは直近10日のみ
dfs_season = [df[df.index >= (datetime.now() + timedelta(days=-10))]
              for df in dfs_season]
dfs_res = [df[df.index >= (datetime.now() + timedelta(days=-10))]
           for df in dfs_res]

# df_flw_1min = pd.read_csv("result_cut_dif.csv",
#                           index_col="time", parse_dates=True)
# df_flw_1min.sort_index(inplace=True)
# def make_multi_timeline(
#     dfs, figname,
#     y_label=None,
#     y_labels=None
# ):
make_multi_timeline(dfs_trend, "trend_multi",
                    y_label="フォロワー数推移トレンド（増減数/分）", y_labels=["@" + df.columns[0] for df in dfs_trend])
make_multi_timeline(dfs_res, "res_multi", y_label="フォロワー数推移残差（増減数/分）",
                    y_labels=["@" + df.columns[0] for df in dfs_res], ylim=dict(bottom=-5, top=5))
make_multi_timeline(dfs_season, "season_multi", y_label="フォロワー数推移周期性成分（増減数/分）",
                    y_labels=["@" + df.columns[0] for df in dfs_season])
