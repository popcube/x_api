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


def start_date_convert(in_str):
    return datetime.strptime(in_str + "T15", f"%Y/%m/%dT%H")


def end_date_convert(in_str):
    return datetime.strptime(in_str + "T21", f"%Y/%m/%dT%H")


def get_event_table():
    pjsekai_res = requests.get("https://pjsekai.com/?2d384281f1")

    a = pd.read_html(pjsekai_res.content, index_col='No', encoding="utf-8",
                     attrs={"id": "sortable_table1"})[0]
    a["ユニット"] = a["ユニット"].apply(unit_name_convert)
    a["開始日"] = a["開始日"].apply(start_date_convert)
    a["終了日"] = a["終了日"].apply(end_date_convert)
    # a.to_csv("./event_data.csv", index=False, header=False)
    return a
