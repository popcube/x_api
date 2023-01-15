from datetime import datetime, timedelta
import pandas as pd
from statsmodels.tsa.seasonal import STL
import sys
from make_js import make_js
import os


def index_UTC_to_JST(df):
    return df.index.to_series().apply(lambda x: x + timedelta(hours=9))


js_name = os.environ.get("JS_NAME")
if js_name is None:
    js_name = "twt_data"
outputter = make_js(js_name)

# read data from csv
df_flw_1min = pd.read_csv("result_cut_dif.csv",
                          index_col="time", parse_dates=True)
df_flw_1min.sort_index(inplace=True)
df_flw_raw_1min = pd.read_csv("results.csv",
                              index_col="fetch_time", parse_dates=True)
df_flw_raw_1min.sort_index(inplace=True)
df_flw_raw_1min.index = index_UTC_to_JST(df_flw_raw_1min)
df_twt = pd.read_csv("twtResults.csv", index_col="time", parse_dates=True, )
df_twt.sort_index(inplace=True)
df_twt.index = index_UTC_to_JST(df_twt)

# resample from 1min to 1H
df_flw = df_flw_1min.resample(
    rule='H', offset=timedelta(seconds=(60/2)*60)).mean()
df_raw = df_flw_raw_1min.resample(
    rule='H', offset=timedelta(seconds=(60/2)*60)).mean()

# resample from 1min to 15min for STL
df_flw_1h = df_flw_1min.resample(
    rule='15min', offset=timedelta(seconds=(15/2)*60)).mean()

# STL decomposition
stl = STL(df_flw_1h['y_cut_diff'], period=24*4, robust=True)
stl_series = stl.fit()
stl_r = stl_series.resid.resample(
    rule='H', offset=timedelta(seconds=(60/2-15/2)*60)).mean()
stl_trend = stl_series.trend.resample(
    rule='H', offset=timedelta(seconds=(60/2-15/2)*60)).mean()

# limit the data range to the available range from follower count log
init_ts = max(df_twt.index[0], df_flw_raw_1min.index[0])
df_twt = df_twt[df_twt.index > init_ts]
df_flw = df_flw[df_flw.index > init_ts]
df_raw = df_raw[df_raw.index > init_ts]
df_trend = stl_trend[stl_trend.index > init_ts]
df_res = stl_r[stl_r.index > init_ts]

outputter.write_js(stl_trend[stl_trend.index > init_ts], "trend_1H")
outputter.write_js(df_raw["followers_count"], "raw_1H")
outputter.write_js(df_flw["y_cut_diff"], "cut_diff_1H")
del outputter
