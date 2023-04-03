from datetime import datetime, timedelta, timezone
import pandas as pd
from statsmodels.tsa.seasonal import STL

from matplotlib import pyplot as plt
from make_timeline import make_timeline
import sys
import os

from make_js import make_js
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

df_twt = pd.read_csv("twtResults.csv", index_col="time", parse_dates=True, )
df_twt.sort_index(inplace=True)
df_twt.index = df_twt.index.to_series().apply(
    lambda x: x + timedelta(hours=9))


def get_y_cut(today):

    x_in = df_flw_1min.loc[today].index.to_list()
    x_res = [df_flw_raw_1min.loc[today].index[0]]
    for i in range(len(x_in) - 1):
        x_res.append(x_in[i] + (x_in[i+1] - x_in[i]) / 2)
    x_res.append(df_flw_raw_1min.loc[today].index[-1])

    y_in = df_flw_1min.loc[today].iloc[:, 0].to_list()
    y_res = [0]
    for i, yd in enumerate(y_in):
        y_res.append(y_res[-1] + yd * (x_res[i+1] -
                     x_res[i]).total_seconds() / 60)

    return x_res, y_res


# today = "2023-01-09"
# make_timeline(df_flw_raw_1min.loc[today].index,
#               df_flw_raw_1min.loc[today].iloc[:, 0], "flw_raw_" + today + "_temp", annot_dfds=df_twt.loc[today])
# print(df_twt.loc[today]["url"].to_list())
today = datetime.now(tz=timezone(offset=timedelta(
    hours=9), name='JST')).strftime("%Y-%m-%d")
if if_day_in_index(datetime.strptime(today, "%Y-%m-%d"), df_twt):
    make_timeline(df_flw_raw_1min.loc[today].index,
                  df_flw_raw_1min.loc[today].iloc[:, 0], "flw_raw_" + today + "_temp", annot_dfds=df_twt.loc[today])
    print(df_twt.loc[today]["url"].to_list())
make_timeline(df_flw_raw_1min.loc[today].index,
              df_flw_raw_1min.loc[today].iloc[:, 0], "flw_raw_" + today + "_vanilla")
y_cut_x, y_cut_y = get_y_cut(today)
# print(len(y_cut_x), len(y_cut_y))
# sys.exit(1)
make_timeline(y_cut_x, y_cut_y, "y_cut_1min_" + today + "_temp")
today = (datetime.now(tz=timezone(offset=timedelta(hours=9),
         name='JST')) + timedelta(days=-1)).strftime("%Y-%m-%d")
print(datetime.strptime(today, "%Y-%m-%d"))
if if_day_in_index(datetime.strptime(today, "%Y-%m-%d"), df_twt):
    make_timeline(df_flw_raw_1min.loc[today].index,
                  df_flw_raw_1min.loc[today].iloc[:, 0], "flw_raw_" + today + "_temp", annot_dfds=df_twt.loc[today])
    print(df_twt.loc[today]["url"].to_list())
make_timeline(df_flw_raw_1min.loc[today].index,
              df_flw_raw_1min.loc[today].iloc[:, 0], "flw_raw_" + today + "_vanilla")
y_cut_x, y_cut_y = get_y_cut(today)
make_timeline(y_cut_x, y_cut_y, "y_cut_1min_" + today + "_temp")
today = datetime.now(tz=timezone(offset=timedelta(
    hours=9), name='JST')).strftime("%Y-%m")
make_timeline(df_flw_raw_1min.loc[today].index,
              df_flw_raw_1min.loc[today].iloc[:, 0], "flw_raw_" + today + "_vanilla")
y_cut_x, y_cut_y = get_y_cut(today)
make_timeline(y_cut_x, y_cut_y, "y_cut_1min_" + today + "_temp")
print(df_twt.loc[today]["url"].to_list())
# sys.exit(0)

df_flw = df_flw_1min.resample(
    rule='15min', offset=timedelta(seconds=(15/2)*60)).mean()
df_raw = df_flw_raw_1min.resample(
    rule='15min', offset=timedelta(seconds=(15/2)*60)).mean()
# print(df_flw)
# df_flw.to_csv("test.csv")
# sys.exit(1)

stl = STL(df_flw['y_cut_diff'], period=24*4, robust=True)
stl_series = stl.fit()
stl_series.plot()
plt.savefig("./STL_decompose.png")
plt.close()

stl_r = stl_series.resid
stl_trend = stl_series.trend
stl_season = stl_series.seasonal
df_res = pd.DataFrame(stl_r)

# make_timeline(stl_r.index, stl_r, "dif_err", y_label="増減量残差")

# ツイートリストの最初とトレンド時系列の最初の時間を揃える（揃えなくていいか）
init_ts = max(df_twt.index[0], df_flw.index[0])

# df_twt = df_twt[df_twt.index > init_ts]
# df_flw = df_flw[df_flw.index > init_ts]
# df_raw = df_raw[df_raw.index > init_ts]
# df_res = df_res.query('index > @init_ts')
# stl_trend = stl_trend[stl_trend.index > init_ts]

df_res.columns = ["res"]
print(df_res)

event_table = None
if account == "pj_sekai":
    event_table = get_event_table()
    # event_table = event_table[event_table["ユニット"] != "mix"]
    event_table = event_table[["ユニット", "開始日", "終了日", "参加人数"]]
    event_table["color"] = event_table["ユニット"].apply(unit_to_color)
    event_table.columns = ["unit", "start_date",
                           "end_date", "participants", "color"]
    # print(event_table.head(5))


# print(event_table.head(30))

make_timeline(df_res.index, df_res["res"], 'res_diff',
              y_label="増減量残差")
make_timeline(stl_trend.index, stl_trend, 'trend_diff',
              y_label="増減量（/分）トレンド", event_hline=event_table)
make_timeline(stl_season.index, stl_season, 'season_diff',
              y_label="増減量（/分）周期成分")

stl_trend.to_csv("trend_diff.csv")
stl_r.to_csv("res_diff.csv")
stl_season.to_csv("season_diff.csv")

# event_timestamps = pd.Series(index=[
#     datetime(2022, 12, 19, 21),
#     datetime(2022, 12, 21, 15), datetime(2022, 12, 29, 21),
#     datetime(2022, 12, 31, 15), datetime(2023, 1, 8, 21),
#     datetime(2023, 1, 10, 15), datetime(2023, 1, 19, 21),
#     datetime(2023, 1, 21, 15), datetime(2023, 1, 29, 21),
#     datetime(2023, 1, 31, 15), datetime(2023, 2, 8, 21),
#     datetime(2023, 2, 10, 15), datetime(2023, 2, 17, 21),
#     datetime(2023, 2, 19, 15)
# ], dtype='int')
# make_timeline(stl_trend[stl_trend.index > init_ts].index,
#               stl_trend[stl_trend.index > init_ts],
#               'trend_diff_annot',
#               y_label="増減量（/分）トレンド",
#               annot_dfds=event_timestamps)
# make_timeline(df_flw_raw_1min[df_flw_raw_1min.index > init_ts].index,
#               df_flw_raw_1min[df_flw_raw_1min.index > init_ts].iloc[:, 0],
#               'raw_1min_eventannot',
#               y_label="フォロワー数推移",
#               annot_dfds=event_timestamps)

# outputter.write_js(stl_trend[stl_trend.index > init_ts], "trend_15min")
# outputter.write_js(df_raw["followers_count"], "raw_15min")
# outputter.write_js(df_flw["y_cut_diff"], "cut_diff_15min")
# del outputter
sys.exit(0)

df_twt_index_str = " ".join(df_twt.index.to_series().apply(str))

for year in set(df_res.index.year):
    month_list = set(df_res.loc[str(year)].index.month)
    for month in month_list:
        day_list = set(df_res.loc[f'{year}-{month}'].index.day)
        for day in day_list:
            today = f'{year}-{month:02d}-{day:02d}'
            df_res_day = df_res.loc[today]

            annot_dfds = pd.Series(dtype=float)
            if today in df_twt_index_str:
                annot_dfds = df_twt.loc[today]

            print(*annot_dfds)
            print(today)
            make_timeline(df_res_day.index,
                          df_res_day["res"], f'res_diff_{today}', annot_dfds=annot_dfds, y_label=f'増減量残差 {today}', interp=True)
            make_timeline(df_flw.loc[today].index,
                          df_flw.loc[today]["y_cut_diff"], f'cut_diff_{today}', annot_dfds=annot_dfds, y_label=f'フォロワー数増減量フィルター後 {today}')

            # if today == '2022-12-30':
            #     window_min = datetime(2022, 12, 30, 11)
            #     window_max = datetime(2022, 12, 30, 13)
            #     window_min2 = datetime(2022, 12, 29, 11)
            #     window_max2 = datetime(2022, 12, 31, 13)
            #     df_flw_1min_temp = df_flw_1min.query(
            #         '@window_min <= index and index <= @window_max')
            #     make_timeline(df_flw_1min_temp.index,
            #                   df_flw_1min_temp["y_cut_diff"], f'flw_diff_{today}_temp', annot_dfds=annot_dfds[:7])
            #     print(df_twt.loc[today]["url"][:7].to_list())

            #     df_flw_1min_temp = df_flw_1min.query(
            #         '@window_min2 <= index and index <= @window_max2')
            #     make_timeline(df_flw_1min_temp.index,
            #                   df_flw_1min_temp["y_cut_diff"], f'flw_diff_{today}_temp2', annot_dfds=annot_dfds[:7])

            #     df_flw_raw_temp = df_flw_raw_1min.query(
            #         '@window_min <= index and index <= @window_max')
            #     make_timeline(df_flw_raw_temp.index,
            #                   df_flw_raw_temp["followers_count"], f'flw_raw_{today}_temp', annot_dfds=annot_dfds[:7])

            #     df_flw_raw_temp = df_flw_raw_1min.query(
            #         '@window_min2 <= index and index <= @window_max2')
            #     make_timeline(df_flw_raw_temp.index,
            #                   df_flw_raw_temp["followers_count"], f'flw_raw_{today}_temp2', annot_dfds=annot_dfds[:7])

            # if today == '2023-01-01':
            #     window_min3 = datetime(2022, 12, 31, 23)
            #     window_max3 = datetime(2023, 1, 1, 2)
            #     df_flw_1min_temp = df_flw_1min.query(
            #         '@window_min3 <= index and index <= @window_max3')
            #     make_timeline(df_flw_1min_temp.index,
            #                   df_flw_1min_temp["y_cut_diff"], f'flw_diff_{today}_temp3', annot_dfds=annot_dfds[:1])

            #     df_flw_raw_temp = df_flw_raw_1min.query(
            #         '@window_min3 <= index and index <= @window_max3')
            #     make_timeline(df_flw_raw_temp.index,
            #                   df_flw_raw_temp["followers_count"], f'flw_raw_{today}_temp3', annot_dfds=annot_dfds[:1])

            # if today == '2023-01-03':
            #     window_min3 = datetime(2023, 1, 3, 11)
            #     window_max3 = datetime(2023, 1, 3, 16)
            #     df_flw_1min_temp = df_flw_1min.query(
            #         '@window_min3 <= index and index <= @window_max3')
            #     make_timeline(df_flw_1min_temp.index,
            #                   df_flw_1min_temp["y_cut_diff"], f'flw_diff_{today}_temp4', annot_dfds=annot_dfds[:9])

            #     df_flw_raw_temp = df_flw_raw_1min.query(
            #         '@window_min3 <= index and index <= @window_max3')
            #     make_timeline(df_flw_raw_temp.index,
            #                   df_flw_raw_temp["followers_count"], f'flw_raw_{today}_temp4', annot_dfds=[])

            #     window_min3 = datetime(2023, 1, 4, 11)
            #     window_max3 = datetime(2023, 1, 4, 16)
            #     df_flw_raw_temp = df_flw_raw_1min.query(
            #         '@window_min3 <= index and index <= @window_max3')
            #     make_timeline(df_flw_raw_temp.index,
            #                   df_flw_raw_temp["followers_count"], f'flw_raw_{today}_temp5', annot_dfds=[])
            #     print(df_twt.loc[today]["url"][:9].to_list())
