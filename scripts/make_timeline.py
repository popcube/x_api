from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import sys
import pandas as pd


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


def make_timeline(x, y, figname, tl=False, y0=False, nan_idxs=[], adjusted_idxs=[]):

    plt.figure(figsize=(15, 8))

    # 移動平均線
    if tl:
        # y_mean10 = pd.Series(y).rolling(10).mean()
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

    plt.gca().set_ylabel("フォロワー数推移", fontname="IPAexGothic")
    plt.gca().tick_params(axis='x', which='major', length=14, color="white")

    x_fill_pairs = make_fill_pairs(x)

    # print(x_fill_pairs)

    for x_fill_pair in x_fill_pairs:
        plt.gca().fill_between(x_fill_pair, [max(y)], [min(y)], fc="#BCECE0")

    # plt.scatter(x, y, edgecolors="black", c="white", zorder=10)
    plt.plot(x, y, c="grey", zorder=1, label="元データ")
    if tl:
        # plt.plot(x, y_mean10, c="orange", linewidth=2,
        #          zorder=5, label="10分移動平均")
        plt.plot(x, y_mean60, c="red", linewidth=2, zorder=10, label="60分移動平均")
        if y0:
            plt.gca().fill_between(x, [max(0, ym) for ym in y_mean60], [
                0] * len(y_mean60), fc="cyan")

    plt.legend(prop={"family": ["IPAexGothic"]})

    # 差分表示のときはnan部を点で表現
    if y[0] == 0:
        plt.axhline(y=0, linestyle="dotted")
        if len(nan_idxs) > 0:
            plt.plot(
                [x[ni] for ni in nan_idxs],
                [y[ni] for ni in nan_idxs],
                marker='o', color="blue", linewidth=0, zorder=20, label="nan idx"
            )
        if len(adjusted_idxs) > 0:
            plt.plot(
                [x[ni] for ni in adjusted_idxs],
                [y[ni] for ni in adjusted_idxs],
                marker='o', color="orange", linewidth=0, zorder=20, label="nan idx"
            )
    # 実数表示の時はnan部を2点間の線で表現
    else:
        for ni in nan_idxs:
            plt.plot([x[ni-1], x[ni]], [y[ni-1], y[ni]],
                     color="blue", zorder=20)
        for ni in adjusted_idxs:
            plt.plot([x[ni-1], x[ni]], [y[ni-1], y[ni]],
                     color="orange", zorder=20)

        # ローカル実行ならグラフ表示、Actions実行ならグラフ保存
    if len(sys.argv) > 1:
        if len(sys.argv) == 2 and sys.argv[1] == "local":
            plt.show()
            return

    plt.savefig(f'./{figname}.png')
    plt.close()
