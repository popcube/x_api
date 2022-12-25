import csv
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd
import sys
from statistics import mean, stdev


def make_fill_pairs(x_in):
    x_datalist_days = (datetime(x_in[-1].year, x_in[-1].month, x_in[-1].day) -
                       datetime(x_in[0].year, x_in[0].month, x_in[0].day)).days
    x_datalist_hours = x_datalist_days * 24 + x_in[-1].hour
    # print(x_in[-1].hour)
    x_datelist = [datetime(x_in[0].year, x_in[0].month, x_in[0].day) +
                  timedelta(hours=1) * i for i in range(x_datalist_hours + 1)]
    x_temp = [xd for xd in x_datelist if xd.hour == 17 or xd.hour == 23]

    # print(x_temp)
    if x_temp[0].hour == 23:
        x_temp.insert(0, x_in[0])
    if x_temp[-1].hour == 17:
        x_temp.append(x_in[-1])

    if len(x_temp) % 2 != 0:
        print("error: x_temp has odd number count!")
        sys.exit(1)

    x_fill_pairs = []
    for i in range(len(x_temp)//2):
        ii = 2*i
        x_fill_pairs.append([x_temp[ii], x_temp[ii+1]])

    return x_fill_pairs

# タイムラインチャート作成


def make_timeline(x, y, tl=False, y0=False):
    plt.figure(figsize=(15, 8))
    # 移動平均線
    if tl:
        y_mean10 = pd.Series(y).rolling(10).mean()
        y_mean60 = pd.Series(y).rolling(60).mean()

    plt.scatter(x, y, c="white")

    xaxis_minor_interval = int(
        (max(x) - min(x)).total_seconds()) // (48 * 60 * 60)
    # print(max(x) - min(x))
    # print(xaxis_minor_interval)

    plt.gca().xaxis.set_major_locator(mdates.HourLocator(byhour=12))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=xaxis_minor_interval))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %a'))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%H'))

    plt.gca().yaxis.set_major_locator(
        ticker.MultipleLocator(max((max(y) - min(y))//600, 0.1) * 100))
    plt.gca().yaxis.set_minor_locator(
        ticker.MultipleLocator(max((max(y) - min(y))//480, 0.1) * 10))
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
    if tl:
        plt.plot(x, y_mean10, c="orange", linewidth=2,
                 zorder=5, label="10分移動平均")
        plt.plot(x, y_mean60, c="red", linewidth=2, zorder=10, label="60分移動平均")
        if y0:
            plt.gca().fill_between(x, y_mean60, [0] * len(y_mean60), fc="cyan")
    plt.legend(prop={"family": ["IPAexGothic"]})


with open("./results.csv") as f:
    rd = list(csv.reader(f))[1:]


data = [[datetime.fromisoformat(
    d[0] + "0") + timedelta(hours=9), int(d[1])] for d in rd]
data.sort(key=lambda x: x[0])

# FOR DEBUG
# data = data[1000:2000]

x = [d[0] for d in data]
y = [d[1] for d in data]

####################
# cut value define #
y_cut_min = -8     #
y_cut_max = 12     #
####################

y_dif = [y[i] - y[i-1] for i in range(1, len(y))]
y_dif_cut = [d for d in y_dif if y_cut_min <= d and d <= y_cut_max]
print(f'mean before cut: {mean(y_dif):.2f}')
print(f'mean after cut: {mean(y_dif_cut):.2f}')

if False:
    ydct = [d for d in y_dif if -1 <= d and d <= 6]
    ydct2 = [d for d in y_dif if (-40 <= d and d < -8) or (12 < d and d <= 40)]
    plt.figure(figsize=(15, 8))
    plt.hist(y_dif, range=(-50, 50), bins=100, label="元の増減量")
    plt.hist(ydct, range=(-50, 50), bins=100, label="自然とみなす範囲")
    plt.hist(ydct2, range=(-50, 50), bins=100, label="ノイズとみなす範囲")
    plt.legend(prop={"family": ["IPAexGothic"]})
    plt.savefig("./ydct.png")
    plt.close()

    def gaussian_func(x, mu, sigma):
        return 1/(sigma * np.sqrt(2 * np.pi)) * np.exp(- (x - mu)**2 / (2 * sigma**2))

    def make_counts(in_data):
        res_counts = dict()
        for d in in_data:
            if str(d) not in res_counts.keys():
                res_counts[str(d)] = 0
            else:
                res_counts[str(d)] += 1
        return res_counts

    ydct_dict = make_counts(ydct)
    ydct2_dict = make_counts(ydct2)
    print(ydct2_dict)
    print("mean(ydct2_dict.values())", mean(ydct2_dict.values()))

    ydct_counts = [d - mean(ydct2_dict.values())
                   for d in ydct_dict.values()]
    ydct_x = list(map(int, ydct_dict.keys()))

    plt.plot(ydct_x, ydct_counts, marker='o', linewidth=0)
    plt.show()

    sys.exit(1)

plt.figure(figsize=(15, 8))
plt.hist(y_dif, range=(-50, 50), bins=100, label="元の増減量")
plt.legend(prop={"family": ["IPAexGothic"]})
plt.savefig("./ori_dif.png")

plt.hist(y_dif_cut, range=(-50, 50), bins=100, label="うち、有効な増減量")
plt.legend(prop={"family": ["IPAexGothic"]})
plt.savefig("./cut_dif.png")
plt.close()

# y_cut_temp_min = y_cut_min
# y_cut_temp_max = y_cut_max
y_cut_dif = [0]
y_base_inc_def = mean(y_dif_cut)
y_base_inc = y_base_inc_def
y_cut_all = y_cut_max - y_cut_min - 2 * y_base_inc_def
adjustee_idxs = {"plus": [], "minus": []}


def yd_valid(yd):
    global y_cut_min
    global y_cut_max
    return (y_cut_min <= yd and yd <= y_cut_max)


def init_bulk():
    global y_base_inc
    global y_cut_all

    y_base_inc = y_base_inc_def
    # y_cut_all = y_cut_max - y_cut_min - 2 * y_base_inc_def
    adjustee_idxs["plus"].clear()
    adjustee_idxs["minus"].clear()


def adjust_bulk():
    # global adjustee_idxs
    global y_base_inc
    global y_cut_dif
    global y_cut_all
    # global y_dif

    if len(adjustee_idxs["plus"]) > 0 and len(adjustee_idxs["minus"]) > 0:
        plus_mean = mean([y_dif[ai] for ai in adjustee_idxs["plus"]])
        minus_mean = mean([y_dif[ai] for ai in adjustee_idxs["minus"]])
        y_base_inc = (plus_mean + minus_mean) / 2
        y_cut_all = plus_mean - y_base_inc
        for ai in adjustee_idxs["plus"]:
            y_cut_dif[ai] = y_dif[ai] - y_cut_all
        for ai in adjustee_idxs["minus"]:
            y_cut_dif[ai] = y_dif[ai] + y_cut_all


nan_count = 0
for i, yd in enumerate(y_dif):
    # 増減量通常時
    if yd_valid(yd):
        y_cut_dif.append(yd)

    # 減少量超過時
    elif yd < y_cut_min:
        yd_temp = yd + y_cut_all
        if yd_valid(yd_temp):
            adjustee_idxs["minus"].append(i)
            adjust_bulk()
            y_cut_dif.append(yd + y_cut_all)
        else:
            y_cut_dif.append(y_base_inc_def)

            print(
                f"exceeded minus in y_cut_all {y_cut_all}, y_base_inc, {y_base_inc}, x {x[i].isoformat()}")
            print(adjustee_idxs)
            nan_count += 1

            init_bulk()
            y_cut_all = - (yd + y_base_inc_def)

    # 増加量超過時
    elif y_cut_max < yd:
        yd_temp = yd - y_cut_all
        if yd_valid(yd_temp):
            adjustee_idxs["plus"].append(i)
            y_cut_dif.append(yd - y_cut_all)
        else:
            y_cut_dif.append(y_base_inc_def)

            print(
                f"exceeded plus in y_cut_all {y_cut_all}, y_base_inc, {y_base_inc}, x {x[i].isoformat()}")
            print(adjustee_idxs)
            nan_count += 1

            init_bulk()
            y_cut_all = yd - y_base_inc_def

print(f"nan_count {nan_count}, nan_ratio {nan_count * 100 / len(data)}%")
# print(len(x), len(y_dif), len(y_cut))

make_timeline(x, [0] + [y[i+1] - y[i]
              for i in range(len(y)-1)], tl=True, y0=True)
plt.savefig("./y_dif.png")
plt.close()

make_timeline(x, y_cut_dif, tl=True, y0=True)
plt.savefig("./y_cut_dif.png")
plt.close()

make_timeline(x, y)
plt.savefig("./y_raw.png")
plt.close()

y_cut = [0]
for yd in y_cut_dif[1:]:
    y_cut.append(y_cut[-1] + yd)
make_timeline(x, y_cut)
plt.savefig("./y_cut.png")
plt.close()
# make_timeline(x, )
