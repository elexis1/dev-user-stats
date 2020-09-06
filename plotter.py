import sys, datetime, numpy
import matplotlib.pyplot as pyplot
import matplotlib.ticker as ticker

def parse_ircstats(lines):

	# values[username][month] = lines/bytes
	values = {}

	# First column is "Date"
	usernames = lines.pop(0).split()[1:]

	for line in lines:
		lvals = line.split()
		month = lvals.pop(0)

		for i in range(len(lvals)):
			username = usernames[i]

			if not username in values:
				values[username] = {}

			values[username][month] = int(lvals[i])

	return usernames, values

def parse_commit_stats(lines, min_year):

	# values[username][month] = lines/bytes
	values = { "Total": {} }
	usernames = ["Total"]

	for line in lines:
		lvals = line.strip().split("\t")
		valcount = len(lvals)
		if valcount == 1:
			month = lvals[0]
		elif valcount == 2:
			year = int(month.split("-")[0])
			if year < min_year:
				continue

			username = lvals[1]
			if not username in usernames:
				usernames.append(username)
				values[username] = {}
			values[username][month] = int(lvals[0])
			
			if not month in values["Total"]:
				values["Total"][month] = 0

			values["Total"][month] += int(lvals[0])

		elif valcount == 0:
			pass
		else:
			raise Exception("Unknown commit stat line:", lvals)

	return usernames, values

def plot_events(events, color, ylim):
	for i in range(len(events)):
		event = events[i]
		x = event[0][0:7] #if month else event[0]
		# TODO: Make this number an equation!
		lines_per_graph = 70
		y = ylim - (i % 5 - 1) * ylim / lines_per_graph 
		pyplot.vlines(x, 0, y, colors = color, linestyles = "solid")
		pyplot.text(x, y, event[1])

def get_linestyle(username, usernames):
	return "dashed" if username == "Total" and len(usernames) > 1 else "solid"

def plot_graph(filename, usernames, commit_values, chat_values, events, print_chat, print_commit, color_project, color_user, figsize, dpi):

	print("Printing " + filename)

	fig, ax1 = pyplot.subplots()

	fig.set_figwidth(figsize[0])
	fig.set_figheight(figsize[1])

	# Print chat statistics
	if print_chat:
		ax1.set_ylabel('chat')
		ax1.minorticks_on()

		for username in usernames:
			ax1.plot(
				chat_values[username].keys(),
				chat_values[username].values(),
				figure = fig,
				label = "chat " + username,
				color = "purple" if username == "Total" and len(usernames) > 1 else "blue",
				linestyle = get_linestyle(username, usernames))

		# Limit graph extents
		ylim = ax1.get_ylim()[1]
		ax1.set_xlim(0, ax1.get_xlim()[1])
		ax1.set_ylim(0, ylim)

		# Add Kilo unit to chat Y axis
		ax1.yaxis.set_major_formatter(ticker.FuncFormatter(
			lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (x * 1e-3) if x >= 1e3 else '%1.0f' % x))

	# Print commit statistics
	if print_commit:
		if print_chat:
			ax2 = ax1.twinx()

		ax = ax2 if print_chat else ax1
		ax.set_ylabel('commit')
		ax.minorticks_on()

		for username in usernames:

			# TODO: UGLY HACK, separate data and code
			if username == "Mythos_Ruler":
				username = "michael"
			elif username == "Philip":
				username = "philip"
			elif username == "stan":
				username = "Stan"
			elif username == "Vladislav":
				username = "vladislavbelov"

			ax.plot(
				commit_values[username].keys(),
				commit_values[username].values(),
				figure = fig,
				label = "commit " + username,
				color = "red" if username == "Total" and len(usernames) > 1 else "green",
				linestyle = get_linestyle(username, usernames)
				)

		# Limit graph extents
		ylim = ax.get_ylim()[1]
		ax.set_xlim(0, ax1.get_xlim()[1])
		ax.set_ylim(0, ylim)

	# Plot project events
	for eventtype in events["project"]:
		plot_events(events["project"][eventtype], color_project, ylim)

	# Plot user events
	for username in events["user"]:
		if username in usernames:
			plot_events(events["user"][username], color_user, ylim)

	# Format axes
	pyplot.xticks(numpy.arange(pyplot.xlim()[0], pyplot.xlim()[1], 4))

	# Print legend
	fig.legend(loc="center left")

	# Save chart
	fig.savefig(filename, dpi=dpi, bbox_inches='tight')
	
	pyplot.close()
