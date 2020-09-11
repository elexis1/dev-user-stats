#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import plot.plotter
import plot.commit_nicknames

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

def plot_commit_stats(fig, ax, usernames, commit_values, color_user, color_total):

    ax.set_ylabel("commit")
    ax.minorticks_on()

    for username in usernames:

        username = plot.commit_nicknames.ircnick_to_commitauthor(username)

        ax.plot(
            commit_values[username].keys(),
            commit_values[username].values(),
            figure = fig,
            label = "commit " + username,
            color = color_total if username == "Total" and len(usernames) > 1 else color_user,
            linestyle = plot.plotter.get_linestyle(username, usernames))

    ax.set_xlim(0, ax.get_xlim()[1])
    ax.set_ylim(0, ax.get_ylim()[1])
