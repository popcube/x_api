import pandas as pd
import requests
from datetime import datetime

import sys


def unit_name_convert(in_str):
    if in_str == "0_VS":
        return "vs"
    elif in_str == "1_L/n":
        return "l/n"
    elif in_str == "2_MMJ":
        return "mmj"
    elif in_str == "3_VBS":
        return "vbs"
    elif in_str == "4_WxS":
        return "wxs"
    elif in_str == "5_25":
        return "n25"
    elif in_str == "混合":
        return "mix"
    else:
        print("unrecognized event type", in_str)
        sys.exit(1)


def date_convert(in_str):
    # return datetime.strptime(in_str + "T15", f"%Y/%m/%dT%H")
    # return datetime.strptime(in_str + "T21", f"%Y/%m/%dT%H")
    return datetime.strptime(in_str, f"%Y/%m/%d")


def get_event_table():
    pjsekai_res = requests.get("https://pjsekai.com/?2d384281f1")

    a = pd.read_html(pjsekai_res.content, index_col='No', encoding="utf-8",
                     attrs={"id": "sortable_table1"})[0]
    a["ユニット"] = a["ユニット"].apply(unit_name_convert)
    a["開始日"] = a["開始日"].apply(date_convert)
    a["終了日"] = a["終了日"].apply(date_convert)
    # a.to_csv("./event_data.csv", index=False, header=False)
    return a


def get_stream_table():
    # pjsekai_res = requests.get("https://pjsekai.com/?1c5f55649f")

    # a = pd.read_html(pjsekai_res.content, encoding="utf-8",
    #                  attrs={"cellpadding": "2", "cellspacing": "2"})

    # aa = a[["No", "配信日時"]]
    # aa.columns = ["No", "配信日時"]
    # aa = aa.drop_duplicates(ignore_index=True)

    # convert Japanese datetime string to datetime object
    # aa["配信日時"] = aa["配信日時"].apply(
    #     lambda x: datetime.strptime(x[:x.index("(")], "%Y/%m/%d"))

    aa = pd.DataFrame([
        ["第27回", datetime(2022, 12, 16)],
        ["第28回", datetime(2023, 1, 27)],
        ["第29回", datetime(2023, 2, 27)],
        ["2.5周年スペシャル", datetime(2023, 3, 23)],
        ["第31回", datetime(2023, 4, 24)],
        ["第32回", datetime(2023, 5, 24)],
        ["第33回", datetime(2023, 6, 19)],
        ["第34回", datetime(2023, 7, 26)],
        ["第35回", datetime(2023, 8, 17)],
        ["3周年スペシャル", datetime(2023, 9, 27)]],
        columns=["No", "配信日時"]
    )

    # Be careful that No column includes the description of the stream
    return aa
