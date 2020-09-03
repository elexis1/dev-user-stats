#!/usr/bin/env python
# -*- coding: utf-8 -*-
import parse_trac_ticket
import dateutil

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

# Weird data bugs in https://trac.wildfiregames.com/: 
# - 2976, 3037 and 3268 have "review" removed or added twice consecutively
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

def print_review_stats(keyword):
    for stat in parse_trac_ticket.count_events(events, keyword, date_format, lambda : dateutil.relativedelta.relativedelta(months=1)):
        print(stat["time"], stat["count"])

#consistency_check("rfc")
#consistency_check("review")
#print_events()
print_review_stats("review")
print_review_stats("rfc")
