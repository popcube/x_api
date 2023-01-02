from datetime import datetime, timedelta
import pandas as pd
from statsmodels.tsa.seasonal import STL
# import statsmodels.api as sm
from matplotlib import pyplot as plt
from make_timeline import make_timeline
import sys

df = pd.read_csv("result_cut_dif.csv", index_col="time", parse_dates=True)
df.sort_index(inplace=True)
# df["index_min"] = df["time"].apply(
#     lambda x: datetime.fromisoformat(x[:-7] + ":00:000"))
# df["index_hour"] = df["time"].apply(
#     lambda x: datetime.fromisoformat(x[:-10] + ":00:00:000"))
# df["index_day"] = df["time"].apply(
#     lambda x: datetime.fromisoformat(x[:-13] + " 00:00:00:000"))
# df = df.set_index(["index_day", "index_hour", "index_min"])


df_twt = pd.read_csv("twtResults.csv", index_col="time", parse_dates=True, )
df_twt.sort_index(inplace=True)
# print(df_twt.head())
df_twt.index = df_twt.index.to_series().apply(
    lambda x: x + timedelta(hours=9))
# print(df_twt.head())
# sys.exit(0)

# print(df)
df_flw = df.resample('15min').mean()
# print(df_flw)
# df_flw.plot()
# plt.show()
# exit()

stl = STL(df_flw['y_cut_diff'], period=24*4, robust=True)
stl_series = stl.fit()
stl_series.plot()
plt.savefig("./STL_decompose.png")
plt.close()

stl_r = stl_series.resid

make_timeline(stl_r.index, stl_r, "dif_err")
# plt.axhline(y=0, linestyle="dotted")

# plt.savefig("./res_err.png")

init_ts = max(df_twt.index[0], df_flw.index[0])
year_list = df_flw.index.year

df_twt = df_twt[df_twt.index > init_ts]
df_flw = df_flw[df_flw.index > init_ts]
# month_list = df_flw.index.month
# day_list = df_flw.index.day
# print(set(year_list), set(mownth_list), set(day_list))

df_twt_index_str = " ".join(df_twt.index.to_series().apply(str))
for year in set(df_flw.index.year):
    month_list = set(df_flw.loc[str(year)].index.month)
    for month in month_list:
        day_list = set(df_flw.loc[f'{year}-{month}'].index.day)
        for day in day_list:
            today = f'{year}-{month}-{day}'
            df_flw_day = df_flw.loc[today]
            # print(" ".join(df_twt_day.index.to_series().apply(str)))
            # print('2022-12-29' in (" ".join(df_twt_day.index.to_series().apply(str))))

            annot_list = []
            if today in df_twt_index_str:
                df_twt_day = df_twt.loc[today]
                annot_list = list(
                    zip(df_twt_day.index, range(1, len(df_twt_day) + 1)))

            print(*annot_list)
            # print(df_tot_day["y_cut_diff"].to_list())
            make_timeline(df_flw_day.index,
                          df_flw_day["y_cut_diff"], f'res_diff_{today}', annot_list=annot_list)
            # sys.exit()
