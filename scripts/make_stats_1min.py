from datetime import datetime, timedelta, timezone
import pandas as pd
from statsmodels.tsa.seasonal import STL

from matplotlib import pyplot as plt
from make_timeline import make_timeline
import sys
import os

# from make_js import make_js
from get_event_table import get_event_table


def unit_to_color(unit):
    unit_color = {
        "vs": "#33CCBB",
        "l/n": "#4455DD",
        "mmj": "#88DD44",
        "vbs": "#EE1166",
        "wxs": "#FF9900",
        "n25": "#884499",
        "mix": "#696969"
    }
    return unit_color[unit]


account = os.environ.get("ACCOUNT")
if not account:
    account = ""

dt_now = datetime.now(tz=timezone(offset=timedelta(hours=9), name='JST'))
dt_today = datetime(dt_now.year, dt_now.month, dt_now.day)
today = dt_today.strftime("%Y-%m-%d")


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


df_flw_1min = pd.read_csv("result_cut_dif.csv",
                          index_col="time", parse_dates=True)
# df_flw_1min.index = pd.to_datetime(df_flw_1min.index)
# TOBE DELETED debug line

df_flw_1min.sort_index(inplace=True)

# outputter.write_js(df_flw_1min.loc["2022-12-28"]
#                    ["y_cut_diff"], "sample_data")
# del outputter
# sys.exit(0)

df_flw_raw_1min = pd.read_csv("results.csv",
                              index_col="fetch_time", parse_dates=True)
df_flw_raw_1min.sort_index(inplace=True)
df_flw_raw_1min.index = df_flw_raw_1min.index.to_series().apply(
    lambda x: x + timedelta(hours=9))

# df_twt = pd.read_csv("twtResults.csv", index_col="time", parse_dates=True, )
# df_twt.sort_index(inplace=True)
# df_twt.index = df_twt.index.to_series().apply(
#     lambda x: x + timedelta(hours=9))


def get_y_cut(today):

    # debug line TOBE DELETED
    # print(df_flw_1min.index.to_list()[-10:])
    # print(type(df_flw_1min.index.to_list()[-1]))
    # print(today)
    # sys.exit(1)

    x_in = df_flw_1min.loc[today].index.to_list()
    x_res = [df_flw_raw_1min.loc[today].index[0]]
    for i in range(len(x_in) - 1):
        x_res.append(x_in[i] + (x_in[i+1] - x_in[i]) / 2)
    if df_flw_raw_1min.loc[today].index[-1] > x_in[-1]:
        x_res.append(df_flw_raw_1min.loc[today].index[-1])
    else:
        x_res.append(pd.Timestamp(today) + timedelta(days=1, seconds=-1))

    y_in = df_flw_1min.loc[today].iloc[:, 0].to_list()
    y_res = [0]
    for i, yd in enumerate(y_in):
        y_res.append(y_res[-1] + yd * (x_res[i+1] -
                     x_res[i]).total_seconds() / 60)

    return x_res, y_res


def get_y_cut_days(days):  # days: int

    df_flw_1min_days = df_flw_1min[df_flw_1min.index >
                                   dt_today + timedelta(-1 * days)]
    df_flw_raw_1min_days = df_flw_raw_1min[df_flw_raw_1min.index >
                                           dt_today + timedelta(-1 * days)]

    x_in = df_flw_1min_days.index.to_list()
    x_res = [df_flw_raw_1min_days.index[0]]
    for i in range(len(x_in) - 1):
        x_res.append(x_in[i] + (x_in[i+1] - x_in[i]) / 2)
    if df_flw_raw_1min_days.index[-1] > x_in[-1]:
        x_res.append(df_flw_raw_1min_days.index[-1])
    else:
        x_res.append(pd.Timestamp(today) + timedelta(days=1, seconds=-1))

    y_in = df_flw_1min_days.iloc[:, 0].to_list()
    y_res = [0]
    for i, yd in enumerate(y_in):
        y_res.append(y_res[-1] + yd * (x_res[i+1] -
                     x_res[i]).total_seconds() / 60)

    return x_res, y_res


days = 32

for iter_day in range(days):
    iter_dt_today = dt_today + timedelta(days=-1 * iter_day)
    iter_today = iter_dt_today.strftime("%Y-%m-%d")
    if if_day_in_index(iter_dt_today, df_flw_raw_1min):
        # if if_day_in_index(iter_dt_today, df_twt):
        #     make_timeline(df_flw_raw_1min.loc[iter_today].index,
        #                   df_flw_raw_1min.loc[iter_today].iloc[:, 0], "flw_raw_" + iter_today + "_temp", annot_dfds=df_twt.loc[iter_today])
        #     print(df_twt.loc[iter_today]["url"].to_list())
        # else:
        make_timeline(df_flw_raw_1min.loc[iter_today].index,
                      df_flw_raw_1min.loc[iter_today].iloc[:, 0], "flw_raw_" + iter_today + "_vanilla")
        y_cut_x, y_cut_y = get_y_cut(iter_today)
        make_timeline(y_cut_x, y_cut_y, "y_cut_1min_" + iter_today + "_temp")

# 以下forループはデータに含まれているか判定するためのもので、iteration目的ではない
days = 32
for iter_day in range(days):
    iter_dt_today = dt_today + timedelta(days=-1 * iter_day)
    if if_day_in_index(iter_dt_today, df_flw_raw_1min):
        df_flw_raw_1min_days = df_flw_raw_1min[df_flw_raw_1min.index >
                                               dt_today + timedelta(-1 * days)]
        make_timeline(df_flw_raw_1min_days.index,
                      df_flw_raw_1min_days.iloc[:, 0], "flw_raw_" + "31days" + "_vanilla")
        y_cut_x, y_cut_y = get_y_cut_days(days)
        make_timeline(y_cut_x, y_cut_y, "y_cut_1min_" + "31days" + "_temp")
        break

df_flw = df_flw_1min.resample(
    rule='15min', offset=timedelta(seconds=(15/2)*60)).mean()
ds_flw = df_flw['y_cut_diff'].dropna()
df_raw = df_flw_raw_1min.resample(
    rule='15min', offset=timedelta(seconds=(15/2)*60)).mean()
ds_raw = df_raw['followers_count'].dropna()
print(df_flw)
df_flw.to_csv("test.csv")

stl = STL(ds_flw, period=24*4, robust=True)
stl_series = stl.fit()
stl_series.plot()
plt.savefig("./STL_decompose.png")
plt.close()

stl_r = stl_series.resid
stl_trend = stl_series.trend
stl_season = stl_series.seasonal

event_table = None
if account == "pj_sekai":
    event_table = get_event_table()
    event_table = event_table[["ユニット", "開始日", "終了日", "参加人数"]]
    event_table["color"] = event_table["ユニット"].apply(unit_to_color)
    event_table.columns = ["unit", "start_date",
                           "end_date", "participants", "color"]

stl_r_10days = stl_r[stl_r.index > dt_today + timedelta(days=-10)]
stl_season_10days = stl_season[stl_season.index >
                               dt_today + timedelta(days=-10)]

make_timeline(stl_r_10days.index, stl_r_10days, 'res_diff',
              y_label="増減量残差", ylim=dict(bottom=-5, top=5))
make_timeline(stl_trend.index, stl_trend, 'trend_diff',
              y_label="増減量（/分）トレンド", event_hline=event_table)
make_timeline(stl_season_10days.index, stl_season_10days, 'season_diff',
              y_label="増減量（/分）周期成分", ylim=dict(bottom=-5, top=5))

# for merge figures
if len(account) > 0:
    stl_trend.to_csv("trend_diff.csv")
    stl_r.to_csv("res_diff.csv")
    stl_season.to_csv("season_diff.csv")
