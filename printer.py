import datetime
import sys
import numpy
import matplotlib.pyplot as pyplot

usernames = sys.stdin.readline().split()[1:]

values = {}

fig = pyplot.figure(num=None, figsize=[25, 15], dpi=100)

for line in sys.stdin:
	lvals = line.split()
	month = lvals.pop(0)

	for i in range(len(lvals)):
		username = usernames[i]

		if not username in values:
			values[username] = {}

		values[username][month] = int(lvals[i])

filtered_usernames = [
	"Total",
	"elexis",
	"leper",
	"wraitii",
#	"stan",
#	"Itms",
]

for username in filtered_usernames:
#	print(username, values[username])
	pyplot.plot(values[username].keys(), values[username].values(), figure=fig, label=username)
#	break

# events
#fig.vlines(4, 0, 5, linestyles ="dotted", colors ="k") 
#fig.vlines(3, 0, 5, linestyles ="solid", colors ="k")
#fig.vlines(5, 0, 5, linestyles ="dashed", colors ="k") 

ylim = pyplot.ylim()[1]

events = [
	["2018-12-23", "Alpha 23b"],
	["2018-05-18", "Alpha 23"],
	["2018-05-03", "leper ban"],
	["2018-12-31", "leper retirement"],
	["2017-10-30", "ban announcement"],
	["2017-10-13", "fatherbushido mimo PM"],
	["2017-07-27", "Alpha 22"],
	["2016-11-08", "Alpha 21"],
	["2016-07-24", "leper email"],
	["2016-06-25", "actually fuck this"],
	["2016-03-31", "Alpha 20"],
	["2015-11-22", "Alpha 19"],
	["2015-03-09", "Alpha 18"]
]

for event in events:
	pyplot.vlines(event[0][0:7], 0, ylim, label=event[1], colors ="k")

pyplot.xlim(0, pyplot.xlim()[1])
pyplot.ylim(0, ylim)

fig.axes[0].minorticks_on()
pyplot.xticks(numpy.arange(pyplot.xlim()[0], pyplot.xlim()[1], 4))

fig.legend(loc="center left")
fig.savefig("/tmp/graph.png", bbox_inches='tight')

