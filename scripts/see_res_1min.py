import csv
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import sys
from statistics import mean

from make_timeline import make_timeline

with open("./results.csv") as f:
    rd = list(csv.reader(f))[1:]

data = [[datetime.fromisoformat(
    d[0] + "0") + timedelta(hours=9), int(d[1])] for d in rd]
data.sort(key=lambda x: x[0])

x = [d[0] for d in data]
y = [d[1] for d in data]

# 12/25 3:00 -
# x = [d[0] for d in data if d[0] > datetime(2022, 12, 25, 3, 0, 0)]
# y = [d[1] for d in data if d[0] > datetime(2022, 12, 25, 3, 0, 0)]

####################
# cut value define #
y_cut_min = -5.5   #
y_cut_max = 12.5   #
####################

y_dif = [0] + [(y[i] - y[i-1]) * 60 / (x[i]-x[i-1]).total_seconds() for i in range(1, len(y))]
x_dif = [x[0]] + [x[i] + (x[i+1] -x[i])/2 for i in range(len(x)-1)]
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
y_cut_dif = []
y_base_inc_def = mean(y_dif_cut)
y_base_inc = y_base_inc_def
y_cut_all = y_cut_max - y_cut_min - 2 * y_base_inc_def
adjustee_idxs = {"plus": [], "minus": []}
nan_idxs = []
adjusted_idxs = set()


def yd_valid(yd):
    # global y_cut_min
    # global y_cut_max
    return (y_cut_min <= yd and yd <= y_cut_max)


def init_bulk():
    global y_base_inc
    # global y_cut_all
    # global adjustee_idxs

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


for i, yd in enumerate(y_dif):
    # 増減量通常時
    if yd_valid(yd):
        y_cut_dif.append(yd)

    # 減少量超過時
    elif yd < y_cut_min:
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

if_adjustee_not_used()

print(
    f"nan_count {len(nan_idxs)}, nan_ratio {len(nan_idxs) * 100 / len(data):.3f}%")
# print(len(x), len(y_dif), len(y_cut))

###### Chart creaation part ######
make_timeline(x_dif, [0] + [y[i+1] - y[i]
              for i in range(len(y)-1)], "y_dif", tl=True, y0=True, nan_idxs=nan_idxs, adjusted_idxs=adjusted_idxs)
make_timeline(x_dif, y_cut_dif, "y_cut_dif", tl=True, y0=True)
make_timeline(x, y, "y_raw", nan_idxs=nan_idxs)

y_cut = [0]
for yd in y_cut_dif[1:]:
    y_cut.append(y_cut[-1] + yd)
make_timeline(x, y_cut, "y_cut")

if len(sys.argv) > 1:
    if len(sys.argv) == 2 and sys.argv[1] == "local":
        sys.exit(0)

df = pd.DataFrame([x_dif, y_cut_dif]).T
df.columns = ["time", "y_cut_diff"]
df.drop(nan_idxs, inplace=True)
df.to_csv("./result_cut_dif.csv", index=False)
