import pandas as pd
import requests

pjsekai_res = requests.get("https://pjsekai.com/?2d384281f1")

a = pd.read_html(pjsekai_res.content, encoding="utf-8",
                 attrs={"id": "sortable_table1"})[0]
a.to_csv("./docs/event_data.csv", index=False, header=False)
