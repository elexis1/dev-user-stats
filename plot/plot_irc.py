#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import plot.plotter
import matplotlib.ticker

def parse_irc_stats(lines):

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

def plot_irc_stats(fig, ax, usernames, irc_values):
    ax.set_ylabel('chat')
    ax.minorticks_on()

    for username in usernames:
        ax.plot(
            irc_values[username].keys(),
            irc_values[username].values(),
            figure = fig,
            label = "chat " + username,
            color = "purple" if username == "Total" and len(usernames) > 1 else "blue",
            linestyle = plot.plotter.get_linestyle(username, usernames))

    # Limit graph extents
    ylim = ax.get_ylim()[1]
    ax.set_xlim(0, ax.get_xlim()[1])
    ax.set_ylim(0, ylim)

    # Add Kilo unit to chat Y axis
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (x * 1e-3) if x >= 1e3 else '%1.0f' % x))

