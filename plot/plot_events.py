#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as pyplot

def plot_events_type(events, color, ylim):
    for i in range(len(events)):
        event = events[i]
        x = event[0][0:7] #if month else event[0]
        # TODO: Make this number an equation!
        lines_per_graph = 70
        y = ylim - (i % 5 - 1) * ylim / lines_per_graph 
        pyplot.vlines(x, 0, y, colors = color, linestyles = "solid")
        pyplot.text(x, y, event[1])

def plot_events(ax, usernames, events, color_project, color_user):

    ylim = ax.get_ylim()[1]

    # Plot project events
    for eventtype in events["project"]:
        plot_events_type(events["project"][eventtype], color_project, ylim)

    # Plot user events
    for username in events["user"]:
        if username in usernames:
            plot_events_type(events["user"][username], color_user, ylim)
