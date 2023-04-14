from datetime import datetime, timedelta, timezone
import pandas as pd
from statsmodels.tsa.seasonal import STL
import sys
from make_js import make_js
import os


def index_UTC_to_JST(df):
    return df.index.to_series().apply(lambda x: x + timedelta(hours=9))


# timezone naive
def get_day_of_last_month(dt):
    last_year = dt.year
    last_month = this_month = dt.month
    if this_month == 1:
        last_year -= 1
        last_month = 12
    else:
        last_month -= 1
    return datetime(last_year, last_month, dt.day)


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

df_raw_all = df_flw_raw_1min.resample(
    rule='D', offset=timedelta(seconds=(24*60/2)*60)).mean()

dt_today = datetime.now(tz=timezone(offset=timedelta(hours=9), name='JST'))
dt_today_lastmonth = get_day_of_last_month(dt_today)
str_yesterday = (datetime(dt_today.year, dt_today.month,
                 dt_today.day) + timedelta(days=-1)).strftime("%Y-%m-%d")

df_flw_1min = df_flw_1min[df_flw_1min.index >= dt_today_lastmonth]
df_flw_raw_1min = df_flw_raw_1min[df_flw_raw_1min.index >= dt_today_lastmonth]
df_twt = df_twt[df_twt.index >= dt_today_lastmonth]
df_flw_1min_yesterday = df_flw_raw_1min.loc[str_yesterday]

# resample from 1min to 1H
df_flw = df_flw_1min.resample(
    rule='H', offset=timedelta(seconds=(60/2)*60)).mean()
df_raw = df_flw_raw_1min.resample(
    rule='H', offset=timedelta(seconds=(60/2)*60)).mean()

# resample from 1min to 15min for STL
df_flw_15min = df_flw_1min.resample(
    rule='15min', offset=timedelta(seconds=(15/2)*60)).mean()

# STL decomposition
stl = STL(df_flw_15min['y_cut_diff'], period=24*4, robust=True)
stl_series = stl.fit()
stl_r = stl_series.resid.resample(
    rule='H', offset=timedelta(seconds=(60/2-15/2)*60)).mean()
stl_trend = stl_series.trend.resample(
    rule='H', offset=timedelta(seconds=(60/2-15/2)*60)).mean()

# limit the data range to the available range from follower count log
# init_ts = max(df_twt.index[0], df_flw_raw_1min.index[0])
# df_twt = df_twt[df_twt.index > init_ts]
# df_flw = df_flw[df_flw.index > init_ts]
# df_raw = df_raw[df_raw.index > init_ts]
# df_trend = stl_trend[stl_trend.index > init_ts]
# df_res = stl_r[stl_r.index > init_ts]

outputter.write_js(stl_trend, "trend_1H")
outputter.write_js(df_raw.iloc[:, 0], "raw_1H")
outputter.write_js(df_flw.iloc[:, 0], "cut_diff_1H")
outputter.write_js(df_flw_1min_yesterday.iloc[:, 0], "raw_1m_yesterday")
del outputter
