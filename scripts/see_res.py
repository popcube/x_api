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
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %A'))
plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%H'))

plt.gca().tick_params(axis='x', which='major', length=14, color="white", width=2)
# plt.gca().set_xticklabels(labels=plt.gca().get_xticklabels(), minor=True)
# plt.gca().grid(which="minor", axis="x")

x_datalist_days = (datetime(x[-1].year, x[-1].month, x[-1].day) - datetime(x[0].year, x[0].month, x[0].day)).days
x_datalist_hours = (x_datalist_days + 1) * 24
x_datelist = [datetime(x[0].year, x[0].month, x[0].day) + timedelta(hours=1) * i for i in range(x_datalist_hours + 2)]
x_temp = []
for x_data in x_datelist:
    if x_data.hour == 17 or x_data.hour == 23:
        x_temp.append(x_data)

print(x_temp)
if x_temp[0].hour == 23:
    x_temp.insert(0, x_datelist[0])
if x_temp[-1].hour == 17:
    x_temp.append(-1, x_datelist[-1])

if len(x_temp) % 2 != 0:
    print("error: x_temp has odd number count!")
    exit

x_fill_pairs = []
for i in range(len(x_temp)//2):
    ii = 2*i
    x_fill_pairs.append([x_temp[ii], x_temp[ii+1]])
    
print(x_fill_pairs)

for x_fill_pair in x_fill_pairs:
    plt.gca().fill_between(x_fill_pair, [max(y)], [min(y)])

plt.show()
