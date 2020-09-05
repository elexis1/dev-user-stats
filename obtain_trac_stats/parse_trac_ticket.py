#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import datetime
import dateutil.parser
import os
import dateutil.relativedelta

# TODO: This is data, not supposed to be here
def getAlias(author):
    if author == "Philip":
        return "philip"
    if author == "gallaecio":
        return "Gallaecio"
    if author == "Josh":
        return "JoshuaJB"
    if author == "Lionkanzen":
        return "Lion_kanzen"
    if author == "stilz_":
        return "stilz"
    return author 

# 2016-05-03-QuakeNet-%230ad-dev.log
# On this day sanderd17 removed 111 review keywords from closed tickets 
# 08:43 < sanderd17> Anyone wondering what tickets I modified: I just removed a number of "review" tags from closed tickets.

def add_event(events, timestamp, author, ticket, action):
    events.append({
        "ticket": ticket,
        "time": timestamp,
        "author": author,
        "action": action
    })

def parse_json(jsline, prefix):
    return json.loads(jsline[len(prefix):-1])

def parse_trac_ticket_old_values(events, old_values):
    author = getAlias(old_values["reporter"])
    ticket = old_values["id"]
    keywords = old_values["keywords"].split()
    timestamp = dateutil.parser.isoparse(old_values["time"])

    # The old_values keywords are wrong, see other comments in this file
    #if "review" in keywords:
    #    add_event(events, timestamp, author, ticket, "created review")

def parse_trac_ticket_change(events, has_review, has_rfc, ticket_open, keywords, old_values, change, had_keyword_changes):
    
    author = getAlias(change["author"])
    fields = change["fields"]
    ticket = old_values["id"]
    timestamp = datetime.datetime.fromtimestamp(change["date"] / 1000 / 1000, datetime.timezone.utc)
    keyword_changes = had_keyword_changes
    
    if "status" in fields:
        new_ticket_open = fields["status"]["new"] != "closed"
        
        # Infer "removed review" when closing a ticket with a review keyword.
        # Avoids 100+ false positive reviews on 2016-05-03.
        if ticket_open and not new_ticket_open and has_review:
            add_event(events, timestamp, author, ticket, "removed review")
            has_review = False
            keyword_changes = True

        ticket_open = new_ticket_open

    if "keywords" in fields:

        old = fields["keywords"]["old"].split()
        new = fields["keywords"]["new"].split()
        keywords = new
        keyword_changes = True

        # PARSE RFC KEYWORD

        # Avoid duplicate events
        if "rfc" in new and not "rfc" in old and not has_rfc:
            add_event(events, timestamp, author, ticket, "added rfc")
            has_rfc = True

        elif "rfc" in old and not "rfc" in new:
            # Infer "added rfc" in case a review keyword was removed but never added
            # trac data bug, (e.g. on #4242), compare with trac emails.
            if not has_rfc:
                add_event(events, timestamp, getAlias(old_values["reporter"]), ticket, "added rfc")
                has_rfc = True

            add_event(events, timestamp, author, ticket, "removed rfc")
            has_rfc = False
            
        # PARSE REVIEWS

        # Avoid duplicate events
        if "review" in new and "review" not in old and not has_review:
            add_event(events, timestamp, author, ticket, "added review")
            has_review = True

        elif "review" in old:

            # Infer "added review" in case a review keyword was removed but never added
            # trac data bug, (e.g. on #4254), compare with trac emails.
            if ticket_open and not had_keyword_changes and ("review" not in new and "review" not in old_values["keywords"].split() or "review" in old):
                add_event(events, dateutil.parser.isoparse(old_values["time"]), getAlias(old_values["reporter"]), ticket, "added review")
                has_review = True

            # Avoid duplicate events
            if has_review and "review" not in new:
                add_event(events, timestamp, author, ticket, "removed review")
                has_review = False

    return keyword_changes, has_review, has_rfc, ticket_open, keywords

def parse_trac_ticket(events, file):
    # This stores the data when the ticket was created
    prefix_old_values = "var old_values="

    # This stores the changes performed to the initial data
    prefix_change = "var changes="

    qbfile = open(file, "r")
    for line in qbfile:
        line = line.strip()

        if line.startswith(prefix_old_values):
            old_values = parse_json(line, prefix_old_values)
            #parse_trac_ticket_old_values(events, old_values)
            ticket_open = True
            keywords = old_values["keywords"]
            had_keyword_changes = False
            has_review = False
            has_rfc = False
        elif line.startswith(prefix_change):
            for change_index, change in enumerate(parse_json(line, prefix_change)):
                keyword_changes, has_review, has_rfc, ticket_open, keywords = parse_trac_ticket_change(events, has_review, has_rfc, ticket_open, keywords, old_values, change, had_keyword_changes)
                if keyword_changes:
                    had_keyword_changes = True
            break

def parse_trac_tickets(directory):
    events = []

    for root, directory, files in os.walk(directory):
        for file in files:
            parse_trac_ticket(events, os.path.join(root, file))

    return events

def sort_trac_events(events, sort_key):
    return sorted(events, key=lambda event: event[sort_key])

def count_open_reviews(events, keyword, group_format, delta):
    return count_trac(
        events,
        keyword,
        group_format,
        delta,
        lambda : 0,
        parse_event_open_reviews,
        lambda current_value : current_value)

def count_review_actions(events, keyword, group_format, delta, action):
    return count_trac(
        events,
        keyword,
        group_format,
        delta,
        lambda : {},
        lambda current_count, event : parse_event_review_action(current_count, event, action),
        lambda current_value : {})

def parse_event_open_reviews(current_count, event):

    if "removed" in event["action"]:
        return current_count - 1

    if "added" in event["action"]:
        return current_count + 1

    return current_count

def parse_event_review_action(current_count, event, action):
    if action in event["action"]:
        author = event["author"]
        if not author in current_count:
            current_count[author] = 0
        current_count[author] += 1
    return current_count

def count_trac(events, keyword, group_format, delta, initial_value, parse_event, next_time_value):

    events = sort_trac_events(events, "time")

    total_count = []

    current_time = None
    current_count = initial_value()

    add_count = lambda time : total_count.append({
        "time": time,
        "count": current_count
    })

    for event in events:
        
        if not keyword is None and not keyword in event["action"]:
            continue

        if current_time == None:
            current_time = event["time"]
        elif event["time"].strftime(group_format) != current_time.strftime(group_format):
            t = current_time
            while t.strftime(group_format) < event["time"].strftime(group_format):
                add_count(t.strftime(group_format))
                t += delta()
            current_time = event["time"]
            current_count = next_time_value(current_count)

        current_count = parse_event(current_count, event)

    add_count(current_time.strftime(group_format))

    return total_count
