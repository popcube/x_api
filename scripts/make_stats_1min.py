from datetime import datetime, timedelta
import pandas as pd
from statsmodels.tsa.seasonal import STL
# import statsmodels.api as sm
from matplotlib import pyplot as plt
from make_timeline import make_timeline
import sys

# df = pd.read_csv("result_cut_dif.csv", index_col="time", parse_dates=True)

# df["index_min"] = df["time"].apply(
#     lambda x: datetime.fromisoformat(x[:-7] + ":00:000"))
# df["index_hour"] = df["time"].apply(
#     lambda x: datetime.fromisoformat(x[:-10] + ":00:00:000"))
# df["index_day"] = df["time"].apply(
#     lambda x: datetime.fromisoformat(x[:-13] + " 00:00:00:000"))
# df = df.set_index(["index_day", "index_hour", "index_min"])


df_twt = pd.read_csv("twtResults.csv", index_col="time", parse_dates=True)
print(df_twt.head())
df_twt.index = df_twt.index.to_series().apply(
    lambda x: datetime.fromisoformat(x) + timedelta(hours=9))
print(df_twt.head())
sys.exit(0)

print(df)
df2 = df.resample('15min').mean()
print(df2)
# df2.plot()
# plt.show()
# exit()

stl = STL(df2['y_cut_diff'], period=24*4, robust=True)
stl_series = stl.fit()
stl_series.plot()
plt.savefig("./STL_decompose.png")
plt.close()

stl_r = stl_series.resid

make_timeline(stl_r.index, stl_r, "res_err.png")
# plt.axhline(y=0, linestyle="dotted")

# plt.savefig("./res_err.png")
