import csv
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import sys
import os
from statistics import mean

from make_timeline import make_timeline

plt.rcParams["font.family"] = "IPAexGothic"
account = os.environ.get("ACCOUNT")


def show_data_stats(time_data):
    minutes_range = (time_data[-1] - time_data[0]).total_seconds() / 60
    data_count = len(time_data)
    data_diffs = [time_data[i] - time_data[i-1]
                  for i in range(1, len(time_data))]
    data_diff_max = max(data_diffs)
    data_diff_min = min(data_diffs)
    diff_max_date = time_data[data_diffs.index(data_diff_max)]
    diff_min_date = time_data[data_diffs.index(data_diff_min)]

    print()
    print("########## data stats ##########")
    print(f'data count: {data_count}, data range: {minutes_range:.2f} min')
    print(
        f'minimum diff: {data_diff_min.total_seconds():.2f} sec at {diff_min_date.isoformat()}')
    print(
        f'maximum diff: {data_diff_max.total_seconds():.2f} sec at {diff_max_date.isoformat()}')
    print("################################")
    print()


with open("./results.csv") as f:
    rd = list(csv.reader(f))[1:]

# change timestamp format to use in python
# and read dynamodb data
data = [[datetime.fromisoformat(
    d[0] + "0") + timedelta(hours=9), int(d[1])] for d in rd]
data.sort(key=lambda x: x[0])

x = [d[0] for d in data]
y = [d[1] for d in data]

show_data_stats(x)
# sys.exit(0)
# 12/25 3:00 -
# x = [d[0] for d in data if d[0] > datetime(2022, 12, 25, 3, 0, 0)]
# y = [d[1] for d in data if d[0] > datetime(2022, 12, 25, 3, 0, 0)]

####################
# define cut value #
y_cut_min = -5.5
y_cut_max = 10.5
if account == "Genshin_7":
    y_cut_min = -5.5
    y_cut_max = 13.5
elif account == "bang_dream_gbp":
    y_cut_min = -11.0
    y_cut_max = 17.0

####################

y_dif = [0] + [(y[i] - y[i-1]) * 60 / (x[i]-x[i-1]).total_seconds()
               for i in range(1, len(y))]
x_dif = [x[0]] + [x[i] + (x[i+1] - x[i])/2 for i in range(len(x)-1)]
y_dif_cut = [d for d in y_dif if y_cut_min <= d and d <= y_cut_max]
print(f'mean before cut: {mean(y_dif):.2f}')
# print(f'mean after cut: {mean(y_dif_cut):.2f}')

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
plt.hist(y_dif, log=True, range=(-50, 50), bins=100, label="元の増減量")
plt.legend()
plt.savefig("./ori_dif.png")

plt.hist(y_dif_cut, log=True,
         range=(-50, 50), bins=100, label="うち、有効な増減量")
plt.legend()
plt.savefig("./cut_dif.png")
plt.close()

# y_cut_temp_min = y_cut_min
# y_cut_temp_max = y_cut_max
y_cut_dif = []
y_base_inc_def = mean(y_dif_cut)
y_base_inc = y_base_inc_def
y_cut_all = y_cut_max - y_cut_min - 2 * y_base_inc_def
adjustee_idxs = {"plus": [], "minus": []}
outlier_idxs = {"plus": [], "minus": []}
nan_idxs = []
adjusted_idxs = set()


def yd_valid(yd):
    return (y_cut_min <= yd and yd <= y_cut_max)


def init_bulk():
    global y_base_inc
    global adjustee_idxs

    y_base_inc = y_base_inc_def
    adjustee_idxs["plus"].clear()
    adjustee_idxs["minus"].clear()


def if_adjustee_not_used():
    # global adjustee_idxs
    global nan_idxs
    if (
        len(adjustee_idxs["plus"]) == 0 or
        len(adjustee_idxs["minus"]) == 0
    ):
        # print(
        #     f"y_cut_all {y_cut_all}, y_base_inc, {y_base_inc}")
        # print(adjustee_idxs)
        nan_idxs += adjustee_idxs["plus"] + adjustee_idxs["minus"]


def adjust_bulk():
    # global adjustee_idxs
    global y_base_inc
    global y_cut_dif
    global y_cut_all
    # global y_dif
    global adjusted_idxs
    global nan_idxs

    # if abs(len(adjustee_idxs["plus"]) - len(adjustee_idxs["minus"])) > 1:
    #     nan_idxs.append(max(adjustee_idxs["plus"] + adjustee_idxs["minus"]))
    #     init_bulk()

    if len(adjustee_idxs["plus"]) > 0 and len(adjustee_idxs["minus"]) > 0:
        adjusted_idxs = set(
            adjustee_idxs["plus"] + adjustee_idxs["minus"] + list(adjusted_idxs))

        plus_mean = mean([y_dif[ai] for ai in adjustee_idxs["plus"]])
        minus_mean = mean([y_dif[ai] for ai in adjustee_idxs["minus"]])
        y_base_inc = (plus_mean + minus_mean) / 2
        y_cut_all = plus_mean - y_base_inc
        for ai in adjustee_idxs["plus"]:
            if len(y_cut_dif) != ai:
                y_cut_dif[ai] = y_dif[ai] - y_cut_all
        for ai in adjustee_idxs["minus"]:
            if len(y_cut_dif) != ai:
                y_cut_dif[ai] = y_dif[ai] + y_cut_all
    elif len(adjustee_idxs["minus"]) > 0:
        y_cut_all = - (y_dif[max(adjustee_idxs["minus"])] - y_base_inc)
    elif len(adjustee_idxs["plus"]) > 0:
        y_cut_all = y_dif[max(adjustee_idxs["plus"])] - y_base_inc


last_memory_timestamp = []
noise_threshold = 10 * 60
for i, yd in enumerate(y_dif):

    # 振動ノイズをその他ノイズに判定するため、前回の振動ノイズ発生時間を記録する
    # 判定閾値は10分
    if len(last_memory_timestamp) == 1:
        if (x_dif[i] - last_memory_timestamp[0]).total_seconds() > noise_threshold:
            if_adjustee_not_used()
            init_bulk()
            y_cut_all = y_cut_max - y_cut_min - 2 * y_base_inc_def

    # 外れ値データ保持は10分前まで
    if len(outlier_idxs["plus"]) > 0:
        if outlier_idxs["plus"][0] < i - 10:
            outlier_idxs["plus"].pop(0)
    if len(outlier_idxs["minus"]) > 0:
        if outlier_idxs["minus"][0] < i - 10:
            outlier_idxs["minus"].pop(0)

    # 増減量通常時
    if yd_valid(yd):
        y_cut_dif.append(yd)
        # if x_dif[i].month == 4 and x_dif[i].day == 3 and x_dif[i].hour == 5 and (x_dif[i].minute >= 37):
        #     print(len(nan_idxs), i, x_dif[i])
        #     print(adjustee_idxs)
        #     print(outlier_idxs)
        #     print(yd, y_cut_min, y_cut_max)

    else:
        last_memory_timestamp = [x_dif[i]]
        # 減少量超過時
        if yd < y_cut_min:
            if yd_valid(yd + y_cut_all):
                adjustee_idxs["minus"].append(i)
                adjust_bulk()
                y_cut_dif.append(yd + y_cut_all)
            else:
                y_cut_dif.append(y_base_inc_def)

                # print(
                #     f"exceeded minus in y_cut_all {y_cut_all}, y_base_inc, {y_base_inc}, x {x[i].isoformat()}")
                # print(adjustee_idxs)

                if_adjustee_not_used()

                init_bulk()
                y_cut_all = - (yd - y_base_inc)
                adjustee_idxs["minus"].append(i)

            outlier_idxs["minus"].append(i)

        # 増加量超過時
        elif y_cut_max < yd:
            if yd_valid(yd - y_cut_all):
                adjustee_idxs["plus"].append(i)
                adjust_bulk()
                y_cut_dif.append(yd - y_cut_all)
            else:
                y_cut_dif.append(y_base_inc_def)

                # print(
                #     f"exceeded plus in y_cut_all {y_cut_all}, y_base_inc, {y_base_inc}, x {x[i].isoformat()}")
                # print(adjustee_idxs)
                if_adjustee_not_used()

                init_bulk()
                y_cut_all = yd - y_base_inc
                adjustee_idxs["plus"].append(i)

            outlier_idxs["plus"].append(i)

        if len(outlier_idxs["plus"]) > 0 and len(outlier_idxs["minus"]) > 0:
            outlier_idxs["plus"].clear()
            outlier_idxs["minus"].clear()

        if len(outlier_idxs["minus"]) >= 5:
            # minus_trend = mean([y_dif[oi] for oi in outlier_idxs["minus"]])
            # for oi in outlier_idxs["minus"]:
            #     if not yd_valid(y_dif[oi] - minus_trend):
            #         break
            # else:
            for oi in outlier_idxs["minus"]:
                if len(y_cut_dif) != oi:
                    y_cut_dif[oi] = y_dif[oi]
                if oi in nan_idxs:
                    nan_idxs.remove(oi)

        if len(outlier_idxs["plus"]) >= 5:
            # plus_trend = mean([y_dif[oi] for oi in outlier_idxs["plus"]])
            # print([y_dif[oi] for oi in outlier_idxs["plus"]])
            # for oi in outlier_idxs["plus"]:
            #     if not yd_valid(y_dif[oi] - plus_trend):
            #         break
            # else:
            for oi in outlier_idxs["plus"]:
                if len(y_cut_dif) != oi:
                    y_cut_dif[oi] = y_dif[oi]
                if oi in nan_idxs:
                    nan_idxs.remove(oi)


if_adjustee_not_used()

print(
    f"nan_count {len(nan_idxs)}, nan_ratio {len(nan_idxs) * 100 / len(data):.3f}%")
# print(len(x), len(y_dif), len(y_cut))

###### Chart creaation part ######
make_timeline(x_dif, y_dif, "y_dif", y0=True,
              nan_idxs=nan_idxs, adjusted_idxs=adjusted_idxs)
make_timeline(x_dif, y_cut_dif, "y_cut_dif", tl=True, y0=True,
              ylim=dict(top=y_cut_max, bottom=y_cut_min))
make_timeline(x, y, "y_raw")
# make_timeline(x, y, "y_raw_annot", nan_idxs=nan_idxs,
#               adjusted_idxs=adjusted_idxs)

x_dif_10days = [xd for xd in x_dif if xd >=
                datetime.now() + timedelta(days=-10)]
y_cut_dif_10days = [ycd for ycd in y_cut_dif[-1 * len(x_dif_10days):]]
make_timeline(x_dif_10days, y_cut_dif_10days, "y_cut_dif_10days", tl=True, y0=True,
              ylim=dict(top=y_cut_max, bottom=y_cut_min))

y_cut = [0]
for i, yd in enumerate(y_cut_dif[1:]):
    y_cut.append(y_cut[-1] + yd * (x[i+1] - x[i]).total_seconds() / 60)
make_timeline(x, y_cut, "y_cut")

if len(sys.argv) > 1:
    if len(sys.argv) == 2 and sys.argv[1] == "local":
        sys.exit(0)

# nan_idxsで15分以上の間隔ができないよう修正
ni = 0
ni_prev = ni
while ni < len(nan_idxs) - 1:
    ni += 1
    if nan_idxs[ni] > nan_idxs[ni-1] + 1:
        ni_prev = ni
        continue
    if (x[nan_idxs[ni]] - x[nan_idxs[ni_prev]]).total_seconds() > 14*60:
        print(
            f"nan_idx {nan_idxs[ni]} ({x_dif[nan_idxs[ni]].isoformat()}) is removed due to no-15-minute-gap rule!")
        y_cut_dif[nan_idxs[ni]] = y_base_inc_def
        del nan_idxs[ni]
        ni_prev = ni

# print(type(x_dif[0]))
df = pd.DataFrame([x_dif, y_cut_dif]).T
df.columns = ["time", "y_cut_diff"]
# on some occasions, Dateteime is not automatically converted to Timestamp
df["time"] = pd.to_datetime(df["time"])
# print(df["time"].dtype)
# print(df["time"])

df.drop(nan_idxs, inplace=True)

# this date format is needed to preserve the format
df.to_csv("./result_cut_dif.csv", index=False,
          date_format="%Y-%m-%d %H:%M:%S.%f")
# df["time"].dt.strftime("%Y-%m-%d %H:%M:%S.%f")
# df.to_csv("./result_cut_dif.csv", index=False)
print("result_cut_dif.csv is saved!")
