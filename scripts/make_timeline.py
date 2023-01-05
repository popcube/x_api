from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import sys
import pandas as pd
from scipy.interpolate import make_interp_spline
import numpy as np


def make_fill_pairs(x_in):
    x_fill_pairs = []
    # print(x_in)

    if len(x_in) == 0:
        return x_fill_pairs

    x_datalist_seconds = (x_in[-1] - x_in[0]).total_seconds()
    # x_datalist_hours = x_datalist_days * 24 + x_in[-1].hour
    # print(x_in[-1].hour)
    x_datelist = [datetime(x_in[0].year, x_in[0].month, x_in[0].day, x_in[0].hour) +
                  timedelta(hours=1) * i for i in range(int(x_datalist_seconds) // 3600 + 2)]
    x_temp = [xd for xd in x_datelist if xd.hour == 17 or xd.hour == 23]

    if len(x_temp) == 0:
        return x_fill_pairs

    # print(x_datelist)
    if x_temp[0].hour == 23:
        x_temp.insert(0, x_in[0])
    if x_temp[-1].hour == 17:
        x_temp.append(x_in[-1])
    # print(x_temp)

    if len(x_temp) % 2 != 0:
        print("error: x_temp has odd number count!")
        sys.exit(1)

    for i in range(len(x_temp)//2):
        ii = 2*i
        x_fill_pairs.append([x_temp[ii], x_temp[ii+1]])

    return x_fill_pairs

# タイムラインチャート作成


def make_timeline(x, y, figname, tl=False, y0=False, nan_idxs=[], adjusted_idxs=[], annot_list=[], y_label="", interp=False):

    plt.figure(figsize=(15, 8))

    # 移動平均線
    if tl:
        # y_mean10 = pd.Series(y).rolling(10).mean()
        y_mean60 = pd.Series(y).rolling(60).mean()

    plt.scatter(x, y, marker='None')

    xaxis_minor_interval = max(
        int((max(x) - min(x)).total_seconds()) // (48 * 60 * 60), 1)
    # print(max(x) - min(x))
    # print(xaxis_minor_interval)

    plt.gca().xaxis.set_major_locator(mdates.HourLocator(byhour=12))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=xaxis_minor_interval))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %a'))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%H'))

    plt.gca().yaxis.set_major_locator(
        ticker.MultipleLocator(max(5*((max(y) - min(y))//60), 1)))
    plt.gca().yaxis.set_minor_locator(
        ticker.MultipleLocator(max((max(y) - min(y))//60, 1) * 1))
    plt.gca().yaxis.set_major_formatter(
        ticker.ScalarFormatter(useOffset=False, useMathText=False))
    plt.gca().yaxis.get_major_formatter().set_scientific(False)

    plt.gca().tick_params(axis='x', which='major', length=14, color="white")

    x_fill_pairs = make_fill_pairs(x)

    # print(x_fill_pairs)

    # アノテーションがないとき（一日毎の表示意外）
    if len(annot_list) == 0:
        plt.plot(x, y, c="grey", zorder=1, label="元データ")
    if tl:
        # plt.plot(x, y_mean10, c="orange", linewidth=2,
        #          zorder=5, label="10分移動平均")
        plt.plot(x, y_mean60, c="red", linewidth=2, zorder=10, label="60分移動平均")
        if y0:
            plt.gca().fill_between(x, [max(0, ym) for ym in y_mean60], [
                0] * len(y_mean60), fc="cyan")

    # 差分表示のときはnan部を点で表現
    if 'dif' in figname:
        if len(y_label) == 0:
            plt.gca().set_ylabel("フォロワー数増減量推移", fontname="IPAexGothic")
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
        if len(y_label) == 0:
            plt.gca().set_ylabel("フォロワー数推移", fontname="IPAexGothic")
        for ni in nan_idxs:
            plt.plot([x[ni-1], x[ni]], [y[ni-1], y[ni]],
                     color="blue", zorder=20)
        for ni in adjusted_idxs:
            plt.plot([x[ni-1], x[ni]], [y[ni-1], y[ni]],
                     color="orange", zorder=20)

    if len(y_label) > 0:
        plt.gca().set_ylabel(y_label, fontname="IPAexGothic")

    # この処理時点でのy軸描画範囲 {最小値、最大値}
    ylim = plt.gca().get_ylim()

    # アノテーションがあるとき（一日毎の表示限定）
    if len(annot_list) > 0:
        # plt.close()
        plt.plot(x, y, marker='o', markerfacecolor='black', markeredgewidth=0,
                 markersize=4, linewidth=0, label="元データ")

        if interp:
            X_Y_Spline = make_interp_spline(
                list(map(lambda ix: ix.timestamp(), x)), y)
            X_ = [min(x) + i * 0.001 * (max(x) - min(x)) for i in range(1001)]
            X_ = list(map(lambda ix: ix.timestamp(), X_))
            Y_ = X_Y_Spline(X_)
            # print(x[:5])
            # print(list(map(datetime.utcfromtimestamp, X_))[:5])
            # sys.exit(9)
            plt.plot(list(map(datetime.utcfromtimestamp, X_)),
                     Y_, c="grey", zorder=1, label="補完曲線")
        else:
            plt.plot(x, y, c="grey", zorder=1)
        # plt.show()
        # sys.exit()
        cm_colors = plt.cm.get_cmap("Dark2").colors
        for i, al in enumerate(annot_list):
            x_text = i / len(annot_list)
            ci = i % len(cm_colors)
            plt.gca().annotate(al[1], xy=(al[0], ylim[1]), size=15, xytext=(
                x_text, 1.05), textcoords='axes fraction',
                bbox={
                    "boxstyle": "circle",
                    "fc": "white",
                    "ec": cm_colors[ci]
            },
                arrowprops={
                    "arrowstyle": "wedge",
                    "color": cm_colors[ci]
            })
            plt.axvline(x=al[0], ymin=0, ymax=1,
                        linestyle="dotted", color=cm_colors[ci])

    for x_fill_pair in x_fill_pairs:
        plt.gca().fill_between(x_fill_pair, *ylim, fc="#BCECE0", zorder=0)

    plt.legend(prop={"family": ["IPAexGothic"]})

    # ローカル実行ならグラフ表示、Actions実行ならグラフ保存
    if len(sys.argv) > 1:
        if len(sys.argv) == 2 and sys.argv[1] == "local":
            plt.show()
            return

    plt.savefig(f'./{figname}.png')
    print(f'./{figname}.png is saved!')
    plt.close()
