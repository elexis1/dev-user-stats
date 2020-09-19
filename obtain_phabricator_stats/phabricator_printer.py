#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
import os
import sys

# The purpose of this script is to print the json data loaded from JSON files to verify data integrity and consistency

# TODO: A comment on a commit has type == "None" but a comments list

def print_subscribers(object, transactions, transaction, authors, authorName, objectName):
    out = ""
    for operation in transaction["fields"]["operations"]:
        operated_author = authors[operation["phid"]]["name"]
        type = operation["operation"]
        if type == "add":
            out += authorName + " added subscriber " + operated_author
        elif type == "add":
            out += authorName + " removed subscriber " + operated_author
        else:
            print("Unknown subscriber action", type, file=sys.stderr)
    return out

def print_accepted(object, transactions, transaction, authors, authorName, objectName):
    return authorName +" accepted " + objectName

def print_concern(object, transactions, transaction, authors, authorName, objectName):
    #committer = authors[transactions[0]["authorPHID"]]["name"]
    return authorName + " raised a concern on " + objectName

def print_comment(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " added a comment to " + objectName

def print_create(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " created " + objectName

def print_inline(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " added an inline comment to " + objectName

def print_status(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " changed status of " + objectName

def print_reviewers(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " changed reviewers of " + objectName

def print_request_changes(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " requested changes to " + objectName

def print_title(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " edited title of " + objectName

def print_summary(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " edited summary of " + objectName

def print_test_plan(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " edited test plan of " + objectName

def print_plan_changes(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " planned changes to " + objectName

def print_request_review(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " requested review of " + objectName

def print_reopen(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " reopened " + objectName

def print_projects(object, transactions, transaction, authors, authorName, objectName):
    # TODO: What is that?
    return authorName + " projects " + objectName

def print_request_verification(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " requested verification of " + objectName

def print_close(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " closed " + objectName

def print_abandon(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " abandoned " + objectName

def print_accepted(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " accepted " + objectName

def print_reclaim(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " reclaimed " + objectName

def print_commandeer(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " commandeered " + objectName

def print_resign(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " resigned from " + objectName

def print_comment(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " commented on " + objectName

def print_update(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " updated " + objectName

def print_subscribers(object, transactions, transaction, authors, authorName, objectName):
    return authorName + " edited subscribers of " + objectName

# See https://server/conduit/method/differential.revision.edit/
transaction_strings = {
    "update": print_update,
    "inline": print_inline,
    "subscribers": print_subscribers,
    "create": print_create,
    "status": print_status,
    "reviewers": print_reviewers,
    "request-changes": print_request_changes,
    "concern": print_concern,
    "title": print_title,
    "summary": print_summary,
    "testPlan": print_test_plan,
    "plan-changes": print_plan_changes,
    "request-review": print_request_review,
    "reopen": print_reopen,
    "projects": print_projects,
    "request-verification": print_request_verification,
    "close": print_close,
    "abandon": print_abandon,
    "accept": print_accepted,
    "reclaim": print_reclaim,
    "commandeer": print_commandeer,
    "resign": print_resign,
    "comment": print_comment
}

def get_date_formatted(epoch, date_format):
    return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc).strftime(date_format)

def print_object_transaction(object, transactions, transaction, authors, date_format):
    
    # These are empty (always?)
    type = transaction["type"]
    if type == None:
        return

    author_phid = transaction["authorPHID"]

    # TODO: Download all authors relating to transactions, not only feeds
    if author_phid == "PHID-APPS-PhabricatorOwnersApplication":
        return

    if not author_phid in authors:
        print(transaction)
        return

    author = authors[author_phid]
    authorName = author["name"]
    if not type in transaction_strings:
        print("Unknown type", type)
        print(transaction)
        return

    objectName = object["fullName"] + " " + object["uri"]

    print(
        get_date_formatted(transaction["dateCreated"], date_format),
        object["name"],
        transaction_strings[type](object, transactions, transaction, authors, authorName, objectName))

def print_all_objects(type, transaction_directory, objects, authors, date_format):

    for object_phid in objects:
        object = objects[object_phid]
        #print(object["uri"], object["fullName"])

        with open(transaction_directory + object_phid + ".json") as transaction_json_string:
            transactions = json.load(transaction_json_string)

            for transaction in transactions:
                if transaction["type"] == type:
                    print_object_transaction(object, transactions, transaction, authors, date_format)

def print_concern_stats(transaction_directory, objects, authors, date_format):

    for object_phid in objects:
        object = objects[object_phid]
        #print(object["uri"], object["fullName"])

        filename = transaction_directory + object_phid + ".json"
        if not os.path.exists(filename):
            # TODO: This can happen for tokens which are part of the feed, but not of transactions
            #print("Object transactions of", object_phid, "have not been downloaded", file=sys.stderr)
            continue

        with open(filename) as transaction_json_string:
            transactions = json.load(transaction_json_string)

            for transaction in transactions:
                author_phid = transaction["authorPHID"]
                
                if author_phid in authors:
                    author = authors[author_phid]
                else:
                    print("Unknown author " + author_phid + " in transaction", transaction, file=sys.stderr)
                    continue

                concernAuthorName = author["name"]

                if transaction["type"] == "concern":
                    concernDate = get_date_formatted(transaction["dateCreated"], date_format)
                    committerName = authors[transactions[0]["authorPHID"]]["name"]
                    print(concernDate, committerName, concernAuthorName, object["name"])
