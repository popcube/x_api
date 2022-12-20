import csv
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd
import sys


def make_fill_pairs(x_in):
    x_datalist_days = (datetime(x_in[-1].year, x_in[-1].month, x_in[-1].day) -
                       datetime(x_in[0].year, x_in[0].month, x_in[0].day)).days
    x_datalist_hours = x_datalist_days * 24 + x_in[-1].hour
    # print(x_in[-1].hour)
    x_datelist = [datetime(x_in[0].year, x_in[0].month, x_in[0].day) +
                  timedelta(hours=1) * i for i in range(x_datalist_hours + 1)]
    x_temp = []
    for x_data in x_datelist:
        if x_data.hour == 17 or x_data.hour == 23:
            x_temp.append(x_data)

    # print(x_temp)
    if x_temp[0].hour == 23:
        x_temp.insert(0, x_in[0])
    if x_temp[-1].hour == 17:
        x_temp.append(-1, x_in[-1])

    if len(x_temp) % 2 != 0:
        print("error: x_temp has odd number count!")
        sys.exit(1)

    x_fill_pairs = []
    for i in range(len(x_temp)//2):
        ii = 2*i
        x_fill_pairs.append([x_temp[ii], x_temp[ii+1]])

    return x_fill_pairs


with open("./results_1min.csv") as f:
    rd = list(csv.reader(f))[1:]


data = [[datetime.fromisoformat(
    d[0] + "0") + timedelta(hours=9), int(d[1])] for d in rd]
data.sort(key=lambda x: x[0])

x = [d[0] for d in data]
y = [d[1] for d in data]
# y2 = [d[2] if d[2] > 7000 else float('NaN') for d in data]

# 移動平均線
y_mean10 = pd.Series(y).rolling(10).mean()
y_mean60 = pd.Series(y).rolling(60).mean()

plt.scatter(x, y, c="white")
# ax2 = plt.gca().twinx()
# ax2.scatter(x, y2, color="orange")
# ax2.plot(x, y2, color="orange")

plt.gca().xaxis.set_major_locator(mdates.HourLocator(byhour=12))
plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=1))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %a'))
plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%H'))
# plt.gca().xaxis.major_ticklabels.set_ha("left")

plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(100))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(100))
plt.gca().yaxis.set_major_formatter(
    ticker.ScalarFormatter(useOffset=False, useMathText=False))
plt.gca().yaxis.get_major_formatter().set_scientific(False)

plt.gca().set_ylabel("フォロワー数", fontname="IPAexGothic")
plt.gca().tick_params(axis='x', which='major', length=14, color="white")

x_fill_pairs = make_fill_pairs(x)

# print(x_fill_pairs)

for x_fill_pair in x_fill_pairs:
    plt.gca().fill_between(x_fill_pair, [max(y)], [min(y)], fc="#BCECE0")

# plt.scatter(x, y, edgecolors="black", c="white", zorder=10)
plt.plot(x, y, c="grey", zorder=1, label="1分毎のデータ")
plt.plot(x, y_mean10, c="orange", linewidth=2, zorder=5, label="10分移動平均")
plt.plot(x, y_mean60, c="red", linewidth=2, zorder=10, label="60分移動平均")
plt.legend(prop={"family": ["IPAexGothic"]})
plt.show()
