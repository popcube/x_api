from datetime import datetime, timedelta
import pandas as pd
from statsmodels.tsa.seasonal import STL

from matplotlib import pyplot as plt
from make_timeline import make_timeline
import sys

df_flw_1min = pd.read_csv("result_cut_dif.csv",
                          index_col="time", parse_dates=True)
df_flw_1min.sort_index(inplace=True)


df_twt = pd.read_csv("twtResults.csv", index_col="time", parse_dates=True, )
df_twt.sort_index(inplace=True)
df_twt.index = df_twt.index.to_series().apply(
    lambda x: x + timedelta(hours=9))


df_flw = df_flw_1min.resample(
    rule='15min', offset=timedelta(seconds=(15/2)*60)).mean()


stl = STL(df_flw['y_cut_diff'], period=24*4, robust=True)
stl_series = stl.fit()
stl_series.plot()
plt.savefig("./STL_decompose.png")
plt.close()

stl_r = stl_series.resid

make_timeline(stl_r.index, stl_r, "dif_err")


init_ts = max(df_twt.index[0], df_flw.index[0])

df_twt = df_twt[df_twt.index > init_ts]
df_flw = df_flw[df_flw.index > init_ts]


df_twt_index_str = " ".join(df_twt.index.to_series().apply(str))

for year in set(df_flw.index.year):
    month_list = set(df_flw.loc[str(year)].index.month)
    for month in month_list:
        day_list = set(df_flw.loc[f'{year}-{month}'].index.day)
        for day in day_list:
            today = f'{year}-{month:02d}-{day:02d}'
            df_flw_day = df_flw.loc[today]

            annot_list = []
            if today in df_twt_index_str:
                df_twt_day = df_twt.loc[today]
                annot_list = list(
                    zip(df_twt_day.index, range(1, len(df_twt_day) + 1)))

                df_flw_day_1min = pd.DataFrame(columns=df_flw_day.columns)
                for ti in df_twt_day.index:
                    window_min = ti - timedelta(minutes=5)
                    window_max = ti + timedelta(minutes=15)
                    df_flw_day_1min = pd.concat([df_flw_day_1min, df_flw_1min.query(
                        '@window_min <= index and index <= @window_max')])
                df_flw_day_1min = df_flw_day_1min[~df_flw_day_1min.index.duplicated(
                )]
                print()
                print(df_flw_day_1min)
                print()

            print(*annot_list)
            print(today)
            make_timeline(df_flw_day.index,
                          df_flw_day["y_cut_diff"], f'res_diff_{today}', annot_list=annot_list)
