from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import STL

from matplotlib import pyplot as plt
from make_timeline import make_timeline, make_multi_timeline
import sys
import os

# from make_js import make_js
from get_table import get_event_table, get_stream_table, get_x_posts


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
    if len(df_res) == 0: return False
    for year in set(df_res.index.year):
        if year != dt.year:
            continue
        month_list = set(df_res.loc[str(year)].index.month)
        for month in month_list:
            if month != dt.month:
                continue
            day_list = set(df_res.loc[f'{year}-{month}'].index.day)
            for day in day_list:
                today = f'{year}-{month:02d}-{day:02d}'
                if dt.strftime("%Y-%m-%d") == today:
                    return True
    else:
        return False

# get the datetime which is closer to the in_datetie in terms of time, ignoring date
# in_datetime_list elements must be in one day


def get_time_in_list(in_datetime, in_datetime_list):
    if len(in_datetime_list) == 0:
        print("in_datetime_list is empty")
        sys.exit(1)
    in_date = in_datetime_list[0].date()
    in_time = in_datetime.time()
    target_datetime = datetime.combine(in_date, in_time)
    return np.abs(np.asarray(in_datetime_list) - target_datetime).argmin()

# outputter = make_js("test_name")


df_flw_1min = pd.read_csv("result_cut_dif.csv",
                          index_col="time", parse_dates=True)
# df_flw_1min.index = pd.to_datetime(df_flw_1min.index)
# TOBE DELETED debug line

df_flw_1min.sort_index(inplace=True)

# last index
df_flw_1min_last_idx = df_flw_1min.tail(1).index[0]

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


days = 11
cut_off_days = 94
iter_dt_days = [dt_today + timedelta(days=-1 * iter_day)
                for iter_day in range(days)]
iter_names = [iter_dt_today.strftime("%Y-%m-%d")
              for iter_dt_today in iter_dt_days]

iter_table = pd.DataFrame()
iter_table["desc"] = iter_names
iter_table["date"] = iter_dt_days
iter_table_backup = pd.DataFrame()

event_table = None
x_post_table = pd.DataFrame(columns=["POST ID", "BODY TEXT", "DETECTED DATE"])
merge_table = pd.DataFrame(columns=["desc", "date"])

if account == "pj_sekai":
    x_post_table = get_x_posts()
    event_table = get_event_table()
    event_table = event_table[["イベント名", "ユニット", "開始日", "終了日", "参加人数"]]
    event_table["color"] = event_table["ユニット"].apply(unit_to_color)
    event_table.columns = ["event_name", "unit", "start_date",
                           "end_date", "participants", "color"]
    stream_table = get_stream_table()
    stream_table.columns = ["No", "date"]

    cut_off_date = dt_today + timedelta(days=-1 * cut_off_days)
    
    if len(event_table) > 0:

        # cut_event_table = event_table[event_table["start_date"] >= cut_off_date]
        cut_event_table = event_table[["event_name", "unit", "start_date"]]
        # merge event_name and unit to create new description for event
        cut_event_table = cut_event_table.apply(lambda x: pd.Series(
            ["【" + x["unit"].upper() + " イベント】" + x["event_name"] + " start date", x["start_date"]]), axis=1)
        cut_event_table.columns = ["desc", "date"]
        # # print(cut_event_table["desc"])
        # cut_event_table_yesterday = cut_event_table.apply(lambda x: x.index, axis=1)
        cut_event_table_yesterday = cut_event_table.apply(lambda x: pd.Series(
            [x["desc"][:-1*len("start date")] + "announcement date", x["date"] + timedelta(days=-1)]), axis=1)
        cut_event_table_yesterday.columns = ["desc", "date"]
        
    else:
        
        cut_event_table = pd.DataFrame(columns=["desc", "date"])
        cut_event_table_yesterday = pd.DataFrame(columns=["desc", "date"])

    # cut_stream_table = stream_table[stream_table["date"] >= cut_off_date]
    stream_table.columns = ["desc", "date"]

    merge_table = pd.concat(
        [cut_event_table, cut_event_table_yesterday, stream_table], ignore_index=True)
    merge_table.sort_values("date", ignore_index=True, inplace=True)

    # duplicated date list
    dupe_dates = merge_table[merge_table.duplicated(subset=["date"])]["date"]
    for dupe_date in dupe_dates:

        # duplicated rows for the same date
        dupe_rows = merge_table[merge_table["date"] == dupe_date]

        # combine the description
        dupe_row_desc = " and " .join(dupe_rows["desc"])

        # set the description to the first duplicated row
        # and delete the rest
        dupe_row_index = dupe_rows.index
        merge_table.loc[dupe_row_index[0], "desc"] = dupe_row_desc
        merge_table.drop(dupe_row_index[1:], inplace=True, axis=0)

    # add datetime info to description
    merge_table.loc[:, "desc"] = merge_table["date"].apply(
        lambda x: x.strftime("%Y-%m-%d ")) + merge_table["desc"]

    # print(merge_table)
    # print(merge_table[merge_table.duplicated(subset=["date"])])

    temp_date_series = pd.concat(
        [iter_table["date"], merge_table["date"]])
    dupe_date_series = temp_date_series[temp_date_series.duplicated()]
    for dupe_date in dupe_date_series:
        iter_table = iter_table[iter_table["date"] != dupe_date]

    iter_table = pd.concat(
        [merge_table[merge_table["date"] >= cut_off_date], iter_table], axis=0)
    # print(iter_table)
    # print(merge_table.duplicated(subset=["date"]))

    # dupe removal logic check
    if len(iter_table[iter_table.duplicated(subset=["date"])]) != 0:
        iter_table = iter_table_backup

if account == "pj_sekai":
    for iter_name, iter_dt_day in iter_table.values:
        iter_name = iter_name.replace("/", "_")
        iter_str_day = iter_dt_day.strftime("%Y-%m-%d")
        if if_day_in_index(iter_dt_day, df_flw_raw_1min) and if_day_in_index(iter_dt_day, df_flw_1min):
            # if if_day_in_index(iter_dt_today, df_twt):
            #     make_timeline(df_flw_raw_1min.loc[iter_today].index,
            #                   df_flw_raw_1min.loc[iter_today].iloc[:, 0], "flw_raw_" + iter_today + "_temp", annot_dfds=df_twt.loc[iter_today])
            #     print(df_twt.loc[iter_today]["url"].to_list())
            # else:
            x_post_day = x_post_table.loc[iter_str_day] if if_day_in_index(iter_dt_day, x_post_table) else False
            df_raw_day = df_flw_raw_1min.loc[iter_str_day].iloc[:, 0]
            make_timeline(df_raw_day.index,
                          df_raw_day,
                          "[raw] " + iter_name,
                          annot_dfds=x_post_day,
                          data_annots=((df_raw_day.idxmax(), df_raw_day.max(), "min"),
                                       (df_raw_day.idxmin(), df_raw_day.min(), "min")))
            y_cut_x, y_cut_y = get_y_cut(iter_str_day)
            annot_idx = get_time_in_list(df_flw_1min_last_idx, y_cut_x)
            make_timeline(y_cut_x,
                          y_cut_y,
                          "[filtered] " + iter_name,
                          annot_dfds=x_post_day,
                          data_annots=[(y_cut_x[annot_idx], y_cut_y[annot_idx], "min")])

    # 以下forループはデータに含まれているか判定するためのもので、iteration目的ではない
    days = 32
    for iter_day in range(days):
        iter_dt_today = dt_today + timedelta(days=-1 * iter_day)
        if if_day_in_index(iter_dt_today, df_flw_raw_1min):
            df_flw_raw_1min_days = df_flw_raw_1min[df_flw_raw_1min.index >
                                                   dt_today + timedelta(-1 * days)].iloc[:, 0]
            # df_flw_raw_1min_days_200m_idx = df_flw_raw_1min_days[df_flw_raw_1min_days >= 2000000].index[0]
            # print(df_flw_raw_1min_days_200m_idx, df_flw_raw_1min_days[df_flw_raw_1min_days_200m_idx])
            # sys.exit(0)
            make_timeline(df_flw_raw_1min_days.index,
                          df_flw_raw_1min_days,
                          "[raw] 31days",
                          data_annots=((df_flw_raw_1min_days.idxmax(), df_flw_raw_1min_days.max(), "max"),
                                       (df_flw_raw_1min_days.idxmin(), df_flw_raw_1min_days.min(), "min")))
            y_cut_x, y_cut_y = get_y_cut_days(days)
            make_timeline(y_cut_x, y_cut_y, "[filtered] 31days")
            break

df_flw = df_flw_1min.resample(
    rule='15min', offset=timedelta(seconds=(15/2)*60)).mean()
ds_flw = df_flw['y_cut_diff'].dropna()
df_raw = df_flw_raw_1min.resample(
    rule='15min', offset=timedelta(seconds=(15/2)*60)).mean()
ds_raw = df_raw['followers_count'].dropna()
print(df_flw)
# df_flw.to_csv("test.csv")

stl = STL(ds_flw, period=24*4, robust=True)
stl_series = stl.fit()
stl_series.plot()
# plt.savefig("./STL_decompose.png")
plt.close()

stl_r = stl_series.resid
stl_trend = stl_series.trend
stl_season = stl_series.seasonal

if account == "pj_sekai":
    event_table["start_date"] = event_table["start_date"].apply(
        lambda x: x + timedelta(hours=15))
    event_table["end_date"] = event_table["end_date"].apply(
        lambda x: x + timedelta(hours=21))

# make_timeline(stl_trend.index, stl_trend, 'trend_diff',
#               y_label="増減量（/分）トレンド", event_hline=event_table)

stl_r_10days = stl_r[stl_r.index > dt_today + timedelta(days=-10)]
stl_season_10days = stl_season[stl_season.index >
                               dt_today + timedelta(days=-10)]
stl_trend_94_days = stl_trend[stl_trend.index > dt_today + timedelta(days=-94)]
# merge_dates_94_days = merge_table[merge_table["date"]
#                                   >= dt_today + timedelta(days=-94)]["date"]
min_max_date_pairs = []
for merge_date in merge_table["date"]:
    # add date as date pair when the date is not the latter part in the pair
    # the first value in the pair is at 00:00:00 while the second value is at 23:59:59
    if merge_date + timedelta(days=-1) not in merge_table["date"].values:
        min_max_date_pairs.append(
            [merge_date, merge_date + timedelta(days=2, seconds=-1)])
# print(min_max_date_pairs)

trend_date_ranges = [stl_trend[(date_pairs[0] <= stl_trend.index) & (
    stl_trend.index <= date_pairs[1])] for date_pairs in min_max_date_pairs]
trend_date_idxmaxs = [(date_range.idxmax(), date_range.max(), "max")
                      for date_range in trend_date_ranges
                      if (len(date_range) > 0)
                      and (date_range.idxmax() != date_range.index[0])
                      and (date_range.idxmax() != date_range.index[-1])]

make_timeline(stl_trend.index, stl_trend, 'trend_diff',
              y_label="増減量（/分）トレンド", event_hline=event_table)

start_date = stl_trend_94_days.index[0]
end_date = stl_trend_94_days.index[-1]

# leap year substitution
if start_date.month == 2 and start_date.day == 29:
    start_date += timedelta(day=-1)
if end_date.month == 2 and end_date.day == 29:
    end_date += timedelta(day=1)


target_time_str = start_date.strftime("%Y-%m-%d %H-%M-%S")
trend_period_df_list = []
trend_period_year_list = []

while True:
    if end_date > stl_trend.index[0]:
        trend_period_df_list.append(
            pd.DataFrame(
                stl_trend[(stl_trend.index > start_date) &
                        (stl_trend.index < end_date)],
                columns=["trend"]
            )
        )
        trend_period_year_list.append(
            str(start_date.year) + "年" if start_date.year == end_date.year else f"{start_date.year}-{end_date.year}年")
    else:
        break
    
    start_date = datetime(start_date.year - 1, start_date.month, start_date.day)
    end_date = datetime(end_date.year - 1, end_date.month, end_date.day)
    
# start_time = datetime(2023, 1, 1, 0, 0, 00)
# end_time = datetime(2023, 4, 1, 0, 0, 00)
# start_time_2 = datetime(2024, 1, 1, 0, 0, 00)
# end_time_2 = datetime(2024, 4, 1, 0, 0, 00)
# start_time_3 = datetime(2025, 1, 1, 0, 0, 00)
# end_time_3 = datetime(2025, 4, 1, 0, 0, 00)

# target_df = trend_df[
#     (trend_df.index > start_time) &
#     (trend_df.index < end_time)
# ]
# target_df_2 = trend_df[
#     (trend_df.index > start_time_2) &
#     (trend_df.index < end_time_2)
# ]
# target_df_3 = trend_df[
#     (trend_df.index > start_time_3) &
#     (trend_df.index < end_time_3)
# ]

def replace_year(in_dt, a, b):
    return datetime.fromisoformat(in_dt.isoformat().replace(str(a), str(b), 1))

# replace year to leap year
leap_year_offset = trend_period_df_list[0].index[-1].year - 2024
for i in range(len(trend_period_df_list)):
    trend_period_df_list[i].index = trend_period_df_list[i].index.to_series().apply(lambda x: replace_year(x, x.year, x.year + i - leap_year_offset))

    print(trend_period_df_list[i])
    
# make_timeline(target_df.index,
#                 target_df.iloc[:, 0],
#                 "[trend] " + target_time_str,
#                 y_label="フォロワー数増減量トレンド")

# print(target_df)
# print(target_df_2)
# print(target_df_3)

make_multi_timeline(
                trend_period_df_list,
                'trend_diff_94_days',
                y_label="フォロワー数増減量トレンド",
                y_labels=trend_period_year_list)
    
# make_timeline(stl_trend_94_days.index, stl_trend_94_days, 'trend_diff_94_days',
#               y_label="増減量（/分）トレンド", event_hline=event_table, data_annots=trend_date_idxmaxs)
make_timeline(stl_r_10days.index, stl_r_10days, 'res_diff_10days',
              y_label="増減量残差", ylim=dict(bottom=-5, top=5))
make_timeline(stl_season_10days.index, stl_season_10days, 'season_diff_10days',
              y_label="増減量（/分）周期成分", ylim=dict(bottom=-5, top=5))


# for merge figures
if len(account) > 0:
    stl_trend.to_csv("trend_diff.csv")
    stl_r.to_csv("res_diff.csv")
    stl_season.to_csv("season_diff.csv")
