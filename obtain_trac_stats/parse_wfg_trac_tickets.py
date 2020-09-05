#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import dateutil
import parse_trac_ticket

# Obtained via wget mirror
directory = "/data/0ad/trac/mirror/trac.wildfiregames.com/ticket/"

# Get statistics grouped per month
date_format = "%Y-%m"

events = parse_trac_ticket.sort_trac_events(parse_trac_ticket.parse_trac_tickets(directory), "time")

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

    events = parse_trac_ticket.sort_trac_events(parse_trac_ticket.parse_trac_tickets(directory), "ticket")

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

sys.stdout = open('../data/trac_events.txt', 'w')
print_events("review")

sys.stdout = open('../data/trac_open_review.txt', 'w')
print_open_review_stats("review")

sys.stdout = open('../data/trac_open_rfc.txt', 'w')
print_open_review_stats("rfc")

sys.stdout = open('../data/trac_added_reviewable_patches.txt', 'w')
print_review_action_stats("review", "added")

sys.stdout = open('../data/trac_performed_reviews.txt', 'w')
print_review_action_stats("review", "removed")
