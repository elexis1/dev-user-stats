#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import phabricator_parser
import phabricator_printer
import os

config_file = "input/phabricator.json"
data_directory = "data/phabricator/"

# output folders
feed_directory = data_directory + "feed/"
author_directory = data_directory + "authors/"
objects_directory = data_directory + "objects/"
transaction_directory = data_directory + "transactions/"
commits_directory = data_directory + "commits/"
objects_filename = objects_directory + "objects.json"

story_limit = 500
sleep_time_story = 4

transaction_limit = 300
sleep_time_transaction = 0.5

object_limit = 500
sleep_time_object = 0.5

commits_limit = 500
sleep_time_commit = 0.5

datetime_format = "%Y-%m-%d %H:%M:%S"
day_format = "%Y-%m-%d"

conduitAPI = None

for directory in [feed_directory, author_directory, objects_directory, transaction_directory, commits_directory]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# DOWNLOAD TASKS
phabricator_parser.load_conduit_API(config_file)
#phabricator_parser.download_all_stories(feed_directory, story_limit, sleep_time_story)
#phabricator_parser.download_all_transactions(feed_directory, transaction_directory, sleep_time_transaction, transaction_limit)
#phabricator_parser.download_all_objects(feed_directory, objects_filename, sleep_time_object, object_limit)
#phabricator_parser.download_all_authors(feed_directory, transaction_directory, author_directory, True)
phabricator_parser.download_all_commits(commit_directory, sleep_time_commit, commits_limit)

# TODO: Download all commits using diffusion.commit.search, download authors therein, so that we can print authors of concerns

# PRINTING TAKS
#objects = phabricator_parser.load_objects(objects_filename)
#authors = phabricator_parser.load_authors(author_directory)
#phabricator_printer.print_all_objects("concern", transaction_directory, objects, authors, datetime_format)
#phabricator_printer.print_concern_stats(transaction_directory, objects, authors, day_format)
