import csv
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates

with open("./results.csv") as f:
    rd = list(csv.reader(f))[1:]


data = [[datetime.fromisoformat(
    d[0] + "0") + timedelta(hours=9), int(d[1]), int(d[3])] for d in rd]
data.sort(key=lambda x: x[0])

x = [d[0] for d in data]
y = [d[1] for d in data]
y2 = [d[2] if d[2] > 7000 else float('NaN') for d in data]

plt.scatter(x, y)
plt.plot(x, y)
# ax2 = plt.gca().twinx()
# ax2.scatter(x, y2, color="orange")
# ax2.plot(x, y2, color="orange")

plt.gca().xaxis.set_major_locator(mdates.DayLocator())
plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=3))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%H'))

plt.gca().tick_params(axis='x', which='major', length=14, color="orange", width=2)
# plt.gca().set_xticklabels(labels=plt.gca().get_xticklabels(), minor=True)
plt.gca().grid(which="minor", axis="x")
plt.show()
