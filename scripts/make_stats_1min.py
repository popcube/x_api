from datetime import datetime
import pandas as pd
from statsmodels.tsa.seasonal import STL
# import statsmodels.api as sm
from matplotlib import pyplot as plt

df = pd.read_csv("result_cut_dif.csv", index_col="time", parse_dates=True)
# df["index_min"] = df["time"].apply(
#     lambda x: datetime.fromisoformat(x[:-7] + ":00:000"))
# df["index_hour"] = df["time"].apply(
#     lambda x: datetime.fromisoformat(x[:-10] + ":00:00:000"))
# df["index_day"] = df["time"].apply(
#     lambda x: datetime.fromisoformat(x[:-13] + " 00:00:00:000"))
# df = df.set_index(["index_day", "index_hour", "index_min"])

print(df)
df2 = df.resample('H').mean()
print(df2)
# df2.plot()
# plt.show()
# exit()

stl = STL(df2['y_cut_diff'], period=24, robust=True)
stl_series = stl.fit()
stl_series.plot()
plt.show()

stl_r = stl_series.resid
stl_r.plot()
plt.axhline(y=0, linestyle="dotted")

plt.show()
