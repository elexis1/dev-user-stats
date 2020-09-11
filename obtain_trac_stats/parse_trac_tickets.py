#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import dateutil
import parse_trac_ticket

# IMPORTANT
# The "review" and "rfc" keywords have (the same) special meaning.
# Inference rules:
# - If a keyword was removed but it hasn't been added before, it is inferred that it was added when the ticket was created.
# - If a ticket is closed that had such a keyword, it is inferred that this keyword was removed by the one closing the ticket on that time.
# - If a keyword is removed twice consecutively, the second removal is ignored.

# 2016-05-03-QuakeNet-%230ad-dev.log
# On this day sanderd17 removed 111 review keywords from closed tickets 
# 08:43 < sanderd17> Anyone wondering what tickets I modified: I just removed a number of "review" tags from closed tickets.


# Obtained via wget mirror
input_directory = "input/trac/ticket/"

output_directory = "data/"

# Get statistics grouped per month
date_format = "%Y-%m"

events = parse_trac_ticket.sort_trac_events(parse_trac_ticket.parse_trac_tickets(input_directory), "time")

def format_date(event):
    return event["time"].strftime("%Y-%m-%d %H:%M:%S");

def print_event(event):
    ticket = "#" + str(event["ticket"])
    date = format_date(event)
    author = event["author"]
    action = event["action"]
    print(date, ticket, author, action)

def print_events(keyword):
    for event in events:
        if keyword is None or keyword in event["action"]:
            print_event(event)

# This allows finding alias names (commit username vs. trac username)
def print_users(keyword):
    authors = []
    for event in events:
        if keyword is None or keyword in event["action"]:
            author = event["author"]
            if not author in authors:
                authors.append(author)

    for author in authors:
        print(author)

# Weird data bugs in https://trac.wildfiregames.com/: 
# 2976, 3037 and 3268 have "review" removed or added twice consecutively
def consistency_check(keyword):
    last_ticket = 0
    count = 0

    events = parse_trac_ticket.sort_trac_events(parse_trac_ticket.parse_trac_tickets(input_directory), "ticket")

    for event in events:
        if last_ticket != event["ticket"]:
            if count % 2 == 1:
                print(last_ticket, count)
            count = 0
            last_ticket = event["ticket"]

        if keyword in event["action"]:
            count += 1
            #print_event(event)

def print_open_review_stats(keyword):
    for stat in parse_trac_ticket.count_open_reviews(events, keyword, date_format, lambda : dateutil.relativedelta.relativedelta(months=1)):
        print(stat["time"], stat["count"])

def print_review_action_stats(keyword, action):
    for stat in parse_trac_ticket.count_review_actions(events, keyword, date_format, lambda : dateutil.relativedelta.relativedelta(months=1), action):
        print(stat["time"])
        author_stats = stat["count"]
        for author in reversed(sorted(author_stats.keys(), key=lambda author: author_stats[author])):
            print("\t", author_stats[author], author)

# This prints tickets for which there are different amounts of keyword added and removed events
#consistency_check("rfc")
#consistency_check("review")

# This can be used to determine alias names 
#print_users("review")

for keyword in ["review", "rfc"]:
	sys.stdout = open(output_directory + "trac_events_" + keyword + ".txt", 'w')
	print_events(keyword)

	sys.stdout = open(output_directory + "trac_open_" + keyword + ".txt", 'w')
	print_open_review_stats(keyword)

	for action in ["added", "removed"]:
		sys.stdout = open(output_directory + "trac_" + action + "_" + keyword + ".txt", 'w')
		print_review_action_stats(keyword, action)
