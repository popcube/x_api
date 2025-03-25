import pandas as pd
import requests
from datetime import datetime

import sys, csv

def get_x_posts(): 
  x_post_table = pd.read_csv(
    "./proseka_x/docs/sorted_data.csv",
    encoding='utf-8',
    encoding_errors='ignore',
    index_col=[0],
    parse_dates=[0,3],
    date_format='ISO8601'
  )
  return x_post_table.sort_index()

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
    datetime_str = in_str.split("*")[0].strip()
    return datetime.strptime(datetime_str, f"%Y/%m/%d")


# def get_event_table():
#     pjsekai_res = requests.get("https://pjsekai.com/?2d384281f1")

#     a = pd.read_html(pjsekai_res.content, index_col='No', encoding="utf-8",
#                      attrs={"id": "sortable_table1"})[0]
#     a["ユニット"] = a["ユニット"].apply(unit_name_convert)
#     a["開始日"] = a["開始日"].apply(date_convert)
#     a["終了日"] = a["終了日"].apply(date_convert)
#     # a.to_csv("./event_data.csv", index=False, header=False)
#     return a

def get_event_table():
    try:
        pjsekai_res = requests.get("https://pjsekai.com/?2d384281f1")
        if pjsekai_res.ok:

            a = pd.read_html(pjsekai_res.content, index_col='No', encoding="utf-8",
                            attrs={"id": "sortable_table1"})[0]
            # default columns belown
            # No, 週目, イベント名, 形式, ユニット, タイプ, 書き下ろし楽曲, 開始日, 終了日, 日数, 参加人数
            
            # a["ユニット"] = a["ユニット"].apply(unit_name_convert)
            # a["開始日"] = date_convert(a, start=True)
            # a["終了日"] = date_convert(a, end=True)
            a["ユニット"] = a["ユニット"].apply(unit_name_convert)
            a["開始日"] = a["開始日"].apply(date_convert)
            a["終了日"] = a["終了日"].apply(date_convert)
            

            
            # a.to_csv("./event_data.csv", index=False, header=False)
            return a
        else:
            raise ValueError("status code: " + str(pjsekai_res.status_code))
    except Exception as e:
        print("ERROR at fetchig event table")
        print(e)
        return pd.DataFrame(columns=["開始日", "終了日", "イベント名", "ユニット", "参加人数"])


def get_stream_table():
    
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
    aa.loc[:, "No"] = aa["No"].apply(lambda x: "ワンダショちゃんねる " + x)
    
    try:
        pjsekai_res = requests.get("https://pjsekai.com/?1c5f55649f")
        # print(pjsekai_res.status_code)
        # print(pjsekai_res.content)
        if pjsekai_res.ok:
            a = pd.read_html(pjsekai_res.content, 
                        encoding="utf-8",
                        attrs={"border": "0", "cellspacing": "1", "class": "style_table"})
            # print(a[0])

            a_temp = a[0][["No", "配信日時"]]
            a_temp.columns = ["No", "配信日時"]
            # print(a_temp)
            a_temp = a_temp.drop_duplicates(ignore_index=True)

            # convert Japanese datetime string to datetime object
            a_temp["配信日時"] = a_temp["配信日時"].apply(
                lambda x: datetime.strptime(x[:x.index("(")], "%Y/%m/%d"))
            a_temp.loc[:, "No"] = a_temp["No"].apply(lambda x: "プロセカ放送局 " + x)
            # print(a_temp)
            aa = pd.concat([aa, a_temp])
            aa.reset_index()
            
    except Exception as e:
        print("ERROR at fetchig steams table")
        print(e)

    # Be careful that No column includes the description of the stream
    return aa

# test_table = get_x_posts()
# print(test_table)
# print(test_table.dtypes)
# print(type(test_table.index))