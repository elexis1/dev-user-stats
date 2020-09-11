#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dateutil
import datetime
import plot.trac_nicknames
from scipy.special._ufuncs import cotdg

# ADDITIONAL INFORMATION THAT CAN BE EXTRACTED:
# Did people review other peoples patches or did they add/remove keywords only of their own patches? (wraitii?)
# How long did patches stick in the review queue?
# How many patches were removed from review queue and never updated again (went to waste)?
# List the users sorted by productivity

def parse_trac_open(folder, min_year, keywords):
    #values[month] = count
    values = { "combined" : {} }

    for keyword in keywords:
        values[keyword] = {}
        with open(folder + "trac_open_" + keyword + ".txt") as f:
            for line in f.readlines():
                lvals = line.split()
                month = lvals[0]
                count = int(lvals[1])
                values[keyword][month] = count
                
                if month not in values["combined"]:
                    values["combined"][month] = 0

                values["combined"][month] += count

    return values

def parse_trac_actions(folder, min_year, keywords, actions):
    # values[keyword][action][username][month]= count
    values = { "combined" : {} }

    for keyword in keywords:
        values[keyword] = {}

        for action in actions:
            values[keyword][action] = { "Total": {} }

            with open(folder + "trac_" + action + "_" + keyword + ".txt") as f:
                lines = f.readlines()

            for line in lines:
                lvals = line.strip().split(" ", 1)
                valcount = len(lvals)
                if valcount == 1:
                    month = lvals[0]
                elif valcount == 2:
                    year = int(month.split("-")[0])
                    if year < min_year:
                        continue

                    count = int(lvals[0])
                    username = lvals[1]

                    action_count = values[keyword][action]
                    if not username in action_count:
                        action_count[username] = {}
                    action_count[username][month] = count

                    total = action_count["Total"]
                    if not month in total:
                        total[month] = 0
                    total[month] += count

                    if not action in values["combined"]: 
                        values["combined"][action] = { "Total": {} }
                    combined = values["combined"][action]
                    if not username in combined:
                        combined[username] = {}
                    if not month in combined[username]:
                        combined[username][month] = 0
                    combined[username][month] += count

                    if not month in combined["Total"]:
                        combined["Total"][month] = 0
                    combined["Total"][month] += count

                elif valcount == 0:
                    pass
                else:
                    raise Exception("Unknown commit stat line:", lvals)

    return values

# TODO: Move this to the parser and write it to files
def print_trac_userstats(trac_action_values, keywords, actions):
    for keyword in keywords:
        for action in actions:
            per_month = trac_action_values[keyword][action]
            total = {}
            for username in per_month:
                total[username] = 0
                for month in per_month[username]:
                    total[username] += per_month[username][month]

            for username in reversed(sorted(total.keys(), key=lambda author: total[author])):
                if username == "Total":
                    continue
                print(username, action, total[username])

def plot_trac_open(fig, ax, trac_values, keywords):

    for keyword in keywords:
        ax.plot(
            trac_values[keyword].keys(),
            trac_values[keyword].values(),
            figure = fig,
            label = "trac open " + keyword)

def plot_trac_actions(fig, ax, usernames, trac_values, keywords, actions):

    group_format = "%Y-%m"

    for keyword in keywords:
        for action in actions:
            for username in usernames:
                username = plot.trac_nicknames.ircnick_to_tracauthor(username)
                if not username in trac_values[keyword][action]:
                    if username != "Total":
                        print(username + " never " + action + " " + keyword)
                    continue

                # the combined values are not inserted chronologically, so sort them
                dates, counts = list(zip(*sorted(zip(*[
                    trac_values[keyword][action][username].keys(),
                    trac_values[keyword][action][username].values()
                ]))))

                # insert omitted zeroes, so there won't be false positives in between
                delta = dateutil.relativedelta.relativedelta(months = 1)

                dates = list(dates)
                counts = list(counts)

                i = 1
                while i < len(dates):
                    t1 = datetime.datetime.strptime(dates[i - 1], group_format)
                    t2 = t1 + delta
                    t3 = datetime.datetime.strptime(dates[i], group_format)
                    if t3 > t2:
                        dates.insert(i, t2.strftime(group_format))
                        counts.insert(i, 0)
                    i += 1

                ax.plot(
                    dates,
                    counts,
                    figure = fig,
                    label = "trac " + username + " " + action + " " + keyword)

def set_trac_axes(ax):
    ax.set_ylabel("trac keywords")
    ax.minorticks_on()
    ax.set_xlim(0, ax.get_xlim()[1])
    ax.set_ylim(0, ax.get_ylim()[1])
