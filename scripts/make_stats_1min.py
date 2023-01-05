from datetime import datetime, timedelta
import pandas as pd
from statsmodels.tsa.seasonal import STL

from matplotlib import pyplot as plt
from make_timeline import make_timeline
import sys

df_flw_1min = pd.read_csv("result_cut_dif.csv",
                          index_col="time", parse_dates=True)
df_flw_1min.sort_index(inplace=True)

df_flw_raw = pd.read_csv("results.csv",
                         index_col="fetch_time", parse_dates=True)
df_flw_raw.sort_index(inplace=True)
df_flw_raw.index = df_flw_raw.index.to_series().apply(
    lambda x: x + timedelta(hours=9))


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

# make_timeline(stl_r.index, stl_r, "dif_err", y_label="増減量残差")


init_ts = max(df_twt.index[0], df_flw.index[0])

df_twt = df_twt[df_twt.index > init_ts]
df_flw = df_flw[df_flw.index > init_ts]
df_res = pd.DataFrame(stl_r).query('index > @init_ts')
df_res.columns = ["res"]
print(df_res)

make_timeline(df_res.index, df_res["res"], 'res_diff', y_label="増減量残差")


df_twt_index_str = " ".join(df_twt.index.to_series().apply(str))

for year in set(df_res.index.year):
    month_list = set(df_res.loc[str(year)].index.month)
    for month in month_list:
        day_list = set(df_res.loc[f'{year}-{month}'].index.day)
        for day in day_list:
            today = f'{year}-{month:02d}-{day:02d}'
            df_res_day = df_res.loc[today]

            annot_list = []
            if today in df_twt_index_str:
                df_twt_day = df_twt.loc[today]
                annot_list = list(
                    zip(df_twt_day.index, range(1, len(df_twt_day) + 1)))

                # df_flw_day_1min = pd.DataFrame(columns=df_flw_day.columns)
                # for ti in df_twt_day.index:
                #     window_min = ti - timedelta(minutes=5)
                #     window_max = ti + timedelta(minutes=15)
                #     df_flw_day_1min = pd.concat([df_flw_day_1min, df_flw_1min.query(
                #         '@window_min <= index and index <= @window_max')])
                # df_flw_day_1min = df_flw_day_1min[~df_flw_day_1min.index.duplicated(
                # )]
                # print()
                # print(df_flw_day_1min)
                # print()

            print(*annot_list)
            print(today)
            make_timeline(df_res_day.index,
                          df_res_day["res"], f'res_diff_{today}', annot_list=annot_list, y_label=f'増減量残差 {today}', interp=True)
            continue

            if today == '2022-12-30':
                window_min = datetime(2022, 12, 30, 11)
                window_max = datetime(2022, 12, 30, 13)
                window_min2 = datetime(2022, 12, 29, 11)
                window_max2 = datetime(2022, 12, 31, 13)
                df_flw_1min_temp = df_flw_1min.query(
                    '@window_min <= index and index <= @window_max')
                make_timeline(df_flw_1min_temp.index,
                              df_flw_1min_temp["y_cut_diff"], f'flw_diff_{today}_temp', annot_list=annot_list[:7])
                print(df_twt.loc[today]["url"][:7].to_list())

                df_flw_1min_temp = df_flw_1min.query(
                    '@window_min2 <= index and index <= @window_max2')
                make_timeline(df_flw_1min_temp.index,
                              df_flw_1min_temp["y_cut_diff"], f'flw_diff_{today}_temp2', annot_list=annot_list[:7])

                df_flw_raw_temp = df_flw_raw.query(
                    '@window_min <= index and index <= @window_max')
                make_timeline(df_flw_raw_temp.index,
                              df_flw_raw_temp["followers_count"], f'flw_raw_{today}_temp', annot_list=annot_list[:7])

                df_flw_raw_temp = df_flw_raw.query(
                    '@window_min2 <= index and index <= @window_max2')
                make_timeline(df_flw_raw_temp.index,
                              df_flw_raw_temp["followers_count"], f'flw_raw_{today}_temp2', annot_list=annot_list[:7])

            if today == '2023-01-01':
                window_min3 = datetime(2022, 12, 31, 23)
                window_max3 = datetime(2023, 1, 1, 2)
                df_flw_1min_temp = df_flw_1min.query(
                    '@window_min3 <= index and index <= @window_max3')
                make_timeline(df_flw_1min_temp.index,
                              df_flw_1min_temp["y_cut_diff"], f'flw_diff_{today}_temp3', annot_list=annot_list[:1])

                df_flw_raw_temp = df_flw_raw.query(
                    '@window_min3 <= index and index <= @window_max3')
                make_timeline(df_flw_raw_temp.index,
                              df_flw_raw_temp["followers_count"], f'flw_raw_{today}_temp3', annot_list=annot_list[:1])

            if today == '2023-01-03':
                window_min3 = datetime(2023, 1, 3, 12)
                window_max3 = datetime(2023, 1, 3, 15)
                df_flw_1min_temp = df_flw_1min.query(
                    '@window_min3 <= index and index <= @window_max3')
                make_timeline(df_flw_1min_temp.index,
                              df_flw_1min_temp["y_cut_diff"], f'flw_diff_{today}_temp4', annot_list=annot_list[:9])

                df_flw_raw_temp = df_flw_raw.query(
                    '@window_min3 <= index and index <= @window_max3')
                make_timeline(df_flw_raw_temp.index,
                              df_flw_raw_temp["followers_count"], f'flw_raw_{today}_temp4', annot_list=annot_list[:9])
                print(df_twt.loc[today]["url"][:9].to_list())
