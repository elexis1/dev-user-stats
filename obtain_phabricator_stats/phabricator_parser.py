#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# The purpose of this script is to iterate through the feed and transaction history,
# download all authors and transactions of feed objects,
# cache it where possible.
# Then this data can be summarized on.

# Important: Keep your clock in sync with the remote backend
# Used to decide whether to skip downloading objects

import time
import sys
import os
import json
import datetime
import ConduitAPI
import phabricator_printer

def load_chronokeys(feed_directory):

    chronokeys = {
        "first": None,
        "last": None
    }

    for root, directory, files in os.walk(feed_directory):
        files.sort()
        for file in files:
            with open(root + file) as feed_json_string:
                stories = json.load(feed_json_string)
                update_chronokey_bounds(stories, chronokeys)

    if chronokeys["first"] is not None and chronokeys["last"] is not None:
        return chronokeys

    chronokey = download_most_recent_chronokey()
    return {
        "first": chronokey,
        "last": chronokey
    }

def update_chronokey_bounds(stories, chronokeys):
    for story_phid in stories:
        chronokey = int(stories[story_phid]["chronologicalKey"])
        chronokeys["first"] = chronokey if chronokeys["first"] is None else min(chronokeys["first"], chronokey)
        chronokeys["last"] = chronokey if chronokeys["last"] is None else max(chronokeys["last"], chronokey)
    return chronokeys

def save_json(filename, data):
    print("Saving " + filename)
    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent=1)

def download_most_recent_chronokey():
    results = conduitAPI.queryFeed(0, 1, True)

    for story_phid in results:
        return int(results[story_phid]["chronologicalKey"])

    return None

def download_feed(feed_directory, chronokeys, forwards, story_limit):

    chronokey = chronokeys["last"] if forwards else chronokeys["first"]
    print("Pulling", story_limit, "stories", "after" if forwards else "before", chronokey)

    stories = conduitAPI.queryFeed(chronokey, story_limit, forwards)

    if len(stories) == 0:
        print("No new stories")
        return stories

    first_chronokey = None
    for story_phid in stories:
        chronokey = int(stories[story_phid]["chronologicalKey"])
        if first_chronokey is None:
            first_chronokey = chronokey
        chronokeys["first"] = min(chronokeys["first"], chronokey)
        chronokeys["last"] = max(chronokeys["last"], chronokey)

    save_json(feed_directory + "feed_" + str(first_chronokey) + "_" + str(len(stories)) + ".json", stories)
    return stories

def load_config(config_file):
    with open(config_file) as json_file:
        return json.load(json_file)
    return None

def load_conduit_API(config_file):
    global conduitAPI

    config = load_config(config_file)
    conduitAPI = ConduitAPI.ConduitAPI(
        config["server"],
        config["token"],
        config["acceptInvalidSSLCert"],
        config["timeout"])


def download_all_stories(feed_directory, story_limit, sleep_time_story):

    chronokeys = load_chronokeys(feed_directory)

    for forwards in [False, True]:
        while True:
            stories = download_feed(feed_directory, chronokeys, forwards, story_limit)
            time.sleep(sleep_time_story)
            if len(stories) == 0:
                break

def download_all_authors(feed_directory, transaction_directory, author_directory, skip_existing_authors):

    global conduitAPI

    # Actually not all object transactions end up in the feed.
    # Therefore this does not download all authors of feed transactions, for example package owners.
    print("Obtaining author stats")
    author_phids = load_author_phids_from_feed(feed_directory).union(load_author_phids_from_transactions(transaction_directory))

    if skip_existing_authors:
        for root, directory, files in os.walk(author_directory):
            for file in files:
                with open(root + file) as author_json_string:
                    authors = json.load(author_json_string)
                    for author_phid in authors:
                        author_phids.discard(author_phid)

    if len(author_phids) == 0:
        print("All authors known")
        return

    print("Downloading", len(author_phids), "authors")
    return
    results = conduitAPI.queryPHIDs(list(author_phids))

    if len(results) > 0:
        save_json(author_directory + "authors_" + str(time.time()), results)

def load_author_phids_from_feed(feed_directory):
    author_phids = set()

    for root, directory, files in os.walk(feed_directory):
        for file in files:
            with open(root + file) as feed_json_string:
                stories = json.load(feed_json_string)
                for story_phid in stories:
                    story = stories[story_phid]
                    author_phids.add(story["authorPHID"])

    return author_phids

def load_author_phids_from_transactions(transaction_directory):
    author_phids = set()

    for root, directory, files in os.walk(transaction_directory):
        for file in files:
            with open(root + file) as transaction_json_string:
                transactions = json.load(transaction_json_string)

                for transaction in transactions:
                    author_phids.add(transaction["authorPHID"])

    return author_phids

def has_transaction(transaction_phid, transactions):
    for transaction in transactions:
        if transaction["phid"] == transaction_phid:
            return True
    return False

def has_all_transactions(transaction_phids, transactions):
    for transaction_phid in transaction_phids:
        if not has_transaction(transaction_phid, transactions):
            return False
    return True

def load_transactions_phids(filename, transaction_phids):

    transactions = []
    after = None
    has_transactions = False

    if not os.path.exists(filename):
        return transactions, has_transactions, after

    with open(filename) as transaction_json_string:

        transactions = json.load(transaction_json_string)

        has_transactions = has_all_transactions(transaction_phids, transactions)

        if has_transactions:
            return transactions, has_transactions, after

        # get latest id
        for transaction in transactions:
            id = int(transaction["id"]) 

            # TODO: It seems Phabricator switched before and after?
            if after is None or id < after:
                after = id

    return transactions, has_transactions, after

def download_object_transactions(filename, object_phid, transactions, after, transaction_limit):

    args = {
        "objectIdentifier": object_phid,
        "limit": transaction_limit
    }

    if after is not None:
        args["after"] = int(after)

    result = conduitAPI.queryAPI("/api/transaction.search", args)
    new_transactions = result["data"]

    print("Received", len(new_transactions), "transactions")

    if len(new_transactions) == 0:
        return True, after

    # Sanity check
    for new_transaction in new_transactions:
        for transaction in transactions:
            if new_transaction["id"] == transaction["id"]:
                print("Transaction", transaction["id"], "already exists, algorithm incorrect", file=sys.stderr)

    transactions += new_transactions
    transactions = sorted(transactions, key=lambda transaction: transaction["id"])

    save_json(filename, transactions)

    after = result["cursor"]["after"]

    if after is None:
        return True, after
    
    return False, after

def download_transactions(transaction_directory, object_phid, transaction_phids, sleep_time_transaction, transaction_limit):

    filename = transaction_directory + object_phid + ".json"

    transactions, has_transactions, after = load_transactions_phids(filename, transaction_phids)

    if has_transactions:
        #print("Skipping", object_phid)
        return

    if len(transactions) > 0:
        print("Loaded", len(transactions), "of", len(transaction_phids), "transactions")

    while True:
        time.sleep(sleep_time_transaction)
        finished, after = download_object_transactions(filename, object_phid, transactions, after, transaction_limit)
        if finished:
            return

def load_transaction_phids_from_feed(feed_directory):
    transaction_phids = dict()

    for root, directory, files in os.walk(feed_directory):
        for file in files:
            with open(root + file) as feed_json_string:
                stories = json.load(feed_json_string)
                for story_phid in stories:
                    story = stories[story_phid]
                    object_phid = story["data"]["objectPHID"]
                    if not "transactionPHIDs" in story["data"]:
                        # Tokens are part of the feed, but not transactions.
                        # They shall be queried using "token.given"
                        if story["class"] == "PhabricatorTokenGivenFeedStory":
                            continue
                        print("story has no transactions", story)
                        sys.exit(0)
                    story_transaction_phids = set(story["data"]["transactionPHIDs"].values())
                    if object_phid in transaction_phids:
                        transaction_phids[object_phid] = story_transaction_phids.union(transaction_phids[object_phid])
                    else:
                        transaction_phids[object_phid] = story_transaction_phids

    return transaction_phids

def download_all_transactions(feed_directory, transaction_directory, sleep_time_transaction, transaction_limit):
    transaction_phids = load_transaction_phids_from_feed(feed_directory)

    '''
    for root, directory, files in os.walk(transaction_directory):
        for file in files:
            with open(root + file) as object_json_string:
                objects = json.load(object_json_string)
                for object_phid in objects:
                    transaction_phids.discard(object_phid)
    '''

    i = 0
    for object_phid in transaction_phids:
        i += 1
        print("Downloading", i, "of", len(transaction_phids), "object transactions")
        download_transactions(transaction_directory, object_phid, list(transaction_phids[object_phid]), sleep_time_transaction, transaction_limit)

def load_object_phids_from_feed(feed_directory):
    object_phids = {}

    for root, directory, files in os.walk(feed_directory):
        for file in files:
            with open(root + file) as feed_json_string:
                stories = json.load(feed_json_string)
                for story_phid in stories:
                    story = stories[story_phid]
                    epoch = story["epoch"]
                    object_phid = story["data"]["objectPHID"]
                    if object_phid in object_phids:
                        object_phids[object_phid] = max(epoch, object_phids[object_phid])
                    else:
                        object_phids[object_phid] = epoch

    return object_phids

def load_objects(objects_filename):
    if os.path.exists(objects_filename):
        with open(objects_filename) as json_file:
            return json.load(json_file)
    return {}

def download_all_objects(feed_directory, objects_filename, sleep_time_object, object_limit):
    global conduitAPI

    objects = load_objects(objects_filename)

    # obtain dict from object_phid of all stories, mapping to their latest timestamp each
    feed_object_phids = load_object_phids_from_feed(feed_directory)

    # remove all phids that have been downloaded already with a sufficiently recent timestamp
    for object_phid in list(feed_object_phids.keys()):
        if object_phid in objects and objects[object_phid]["epoch"] >= feed_object_phids[object_phid]:
            #print("Skipping", object_phid)
            feed_object_phids.pop(object_phid)

    while feed_object_phids:
        object_phids = []
        while feed_object_phids and len(object_phids) < object_limit:
            object_phid = next(iter(feed_object_phids))
            feed_object_phids.pop(object_phid)
            object_phids.append(object_phid)

        print("Downloading", len(object_phids), "of", len(feed_object_phids), "objects")
        epoch = time.time()
        results = conduitAPI.queryPHIDs(object_phids)

        for object_phid in results:
            objects[object_phid] = results[object_phid]
            objects[object_phid]["epoch"] = epoch

        save_json(objects_filename, objects)
        time.sleep(sleep_time_object)

def load_authors(author_directory):
    authors = {}
    for root, directory, files in os.walk(author_directory):
        for file in files:
            with open(root + file) as author_json_string:
                authors.update(json.load(author_json_string))

    return authors

def download_commits(after, commit_directory, commits_limit):

    args = {
        "limit": 2#commits_limit
    }

    if after is not None:
        args["after"] = after

    result = conduitAPI.queryAPI("/api/diffusion.commit.search", args)

    commits = result["data"]

    for commit in commits:
        first_commit_id = min(first_commit_id, commit["id"])

    save_json(commit_directory + "commit_" + first_commit_id + "_" + len(commits) + ".json", objects)

    return result["cursor"]["after"]

def download_all_commits(commit_directory, sleep_time_commit, commits_limit):

    commits = {}

    for commit in commits:
        after = max(after, commit["id"])

    # In the first query see if there are any commits aftter the latest one we got.
    # If we didn't download any commits before, we will get the most recent commit first.
    # before = max(commit["id"])
    after = download_commits(commit_directory, commits_limit)

    # Then download all commits until the latest one we have
    # after = min(commit["id"])

    # Notice commit id is different from the repository commit id, since the id can relate to a commit of different repositories

    #for forwards in [False, True]:
