#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import plot.plot_events
import plot.plot_commit
import plot.plot_irc
import plot.plot_trac
import sys
import datetime
import numpy
import matplotlib.pyplot as pyplot
import functools

def get_linestyle(username, usernames):
	return "dashed" if username == "Total" and len(usernames) > 1 else "solid"

def plot_graph(
	filename,
	usernames,
	commit_values,
	irc_values,
	trac_values,
	events,
	print_irc,
	print_commit,
	print_trac_open,
	print_trac_actions,
	print_events,
	keywords,
	actions,
	color_event_project,
	color_event_user,
	color_commit_user,
	color_commit_total,
	figsize,
	dpi):

	print("Printing " + filename)

	ax_count = functools.reduce(lambda sum, p: sum + p, [
		print_commit,
		print_irc,
		print_trac_actions or print_trac_open])
	ax_index = 0

	fig, ax = pyplot.subplots()
	
	axes = [ax]
	for i in range(ax_count - 1):
		ax2 = ax.twinx()
		ax2.spines["right"].set_position(("axes", 1 + i / 20))
		axes.append(ax2)

	fig.set_figwidth(figsize[0])
	fig.set_figheight(figsize[1])

	if print_irc:
		plot.plot_irc.plot_irc_stats(fig, axes[ax_index], usernames, irc_values)
		ax_index += 1

	if print_commit:
		ax = axes[ax_index]
		ax_index += 1
		plot.plot_commit.plot_commit_stats(fig, ax, usernames, commit_values, color_commit_user, color_commit_total)

	if print_trac_actions or print_trac_open:
		ax = axes[ax_index]
		ax_index += 1
		if print_trac_open:
			plot.plot_trac.plot_trac_open(fig, ax, trac_values["open"], ["combined"])
		if print_trac_actions:
			plot.plot_trac.plot_trac_actions(fig, ax, usernames, trac_values["actions"], keywords, actions)
		plot.plot_trac.set_trac_axes(ax)

	if print_events:
		plot.plot_events.plot_events(axes[-1], usernames, events, color_event_project, color_event_user)

	# Format axes
	pyplot.xticks(numpy.arange(pyplot.xlim()[0], pyplot.xlim()[1], 4))

	# Print legend
	fig.legend(loc="center left")

	# Save chart
	fig.savefig(filename, dpi=dpi, bbox_inches='tight')
	
	pyplot.close()
