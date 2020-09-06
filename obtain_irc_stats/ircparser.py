#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, re, sys, getopt
import ircnicknames

# Execution example --mode="chatmessages" --year=2014

# Nickname grammar defined in https://tools.ietf.org/html/rfc2812#section-2.3.1
#  nickname   =  ( letter / special ) *8( letter / digit / special / "-" )
#  special    =  %x5B-60 / %x7B-7D
#                   ; "[", "]", "\", "`", "_", "^", "{", "|", "}"
# Notice: We simplify to
#  nickname   =  ( letter / digit / special / "-" )*9
#
#   While the maximum length is limited to nine characters, clients
#   SHOULD accept longer strings as they may become used in future
#   evolutions of the protocol.

# TODO
# --- Day changed Wed Sep 15 2010
# 11:14 < Username`[m]> Message
# 12:34 -!- username [~username@12.34.56.78] has quit [Quit]

reNickname = '[\@\ \+]?[a-zA-Z0-9\[\]\\\`\_\-\^\{\|\}]{1,50}'

# 12:34
reTimestamp1 = '[0-9]{2}\:[0-9]{2}'

minimum_count = 5

# 12:34:56
#reTimestamp2 = '[0-9]{2}\:[0-9]{2}\:[0-9]{2}'

# arbitrary string
reMessage = '[\S\s]*'

# -!-
reExclamation = '\-\!\-'

# Modes:
# "formatstats": print statistics about how many files use which log format, useful to convert and minimize format differences
# "userstats_total": print statistics on how many messages are sent per user
# "userstats_daily": print statistics on how many messages are sent per user per day
# "userstats_monthly": print statistics on how many messages are sent per user per month
# "userstats_weekly": print statistics on how many messages are sent per user per week
# "chatmessages": print only chat messages, useful to create wordclouds
# "linesperlog": print number of lines per day
# "stats_users": print monthly chat statistics per user, in a table format
mode = "userstats_monthly"

# Either 2003 or 2009
#fileset = "2003"
fileset = "2012"

root_folder = "/data/0ad/meetinglogs_repository/repository/"

filtered_year = None

# filter #0ad where #0ad-dev exists
filtered_dev_channel = True

# number of chatmessages or characters in the current logfile, excluding blacklisted users, including non-filtered users
totalcount = 0

# whether to count lines of chat or also account for the length of each line
count_characters = True

# these users are displayed/filtered each time a file is parsed
filtered_users = None;

# these users are ignored when counting the total number of lines posted
blacklisted_users = None

def parse(filteredusers, blacklistedusers):

	global fileset, root, mode, filtered_users, blacklisted_users
	blacklisted_users = blacklistedusers
	filtered_users = filteredusers

	#parseFiles('/data/0ad/meetinglogs_repository/repository/')

	if not filtered_users is None:
		print("Date", "", end='')
		print("Total", "", end='')
		for username in filtered_users:
			print(username, "", end='')
		print()

	if fileset == "2003":
		parseFiles(root_folder + '2003-06-09 to 2009-07-11 closed source, restricted log')
	else:
		#parseFiles(root_folder + '2009-07-11 to 2012-02-02 public chat, restricted log')
		parseFiles(root_folder + '2012-02-03 to 2019-04-14 public chat, public log')

	if mode == "formatstats":
		print(stats_lineformat)

	elif mode == "userstats_total":
		printUserstats()

def printUserstats():
	global stats_chatmessages

	if filtered_users == None:
		print()
		stats = [(k, stats_chatmessages[k]) for k in sorted(stats_chatmessages, key=stats_chatmessages.get, reverse=True)]
		for username, count in stats:
			if count > minimum_count and (filtered_users is None or (username in filtered_users)) and (blacklisted_users is None or not (username in blacklisted_users)):
				print(username, count)
	else:
		print(totalcount, "", end = '')
		for username in filtered_users:
			if username in stats_chatmessages:
				print(stats_chatmessages[username], "", end = '')
			else:
				print(0, "", end = '')
		print()

# 12:34 <nickname> message
# or
# 12:34 < nickname> message
# 12:34 <@nickname> message
# 12:34 <+nickname> message
def parseLineTimestampChat(line):
	reg = '(' + reTimestamp1 + ')\ \<(' + reNickname + ')\>\ (' + reMessage + ')'
	#print(reg)
	#sys.exit()
	p = re.compile(reg)

	result = p.fullmatch(line)

	if result is None:
		return None

	global stats_chatmessages, totalcount, count_characters

	username = ircnicknames.getUsername(result.group(2))

	if count_characters:	
		diff = len(result.group(3))
	else:
		diff = 1

	stats_chatmessages[username] = stats_chatmessages[username] + diff if username in stats_chatmessages else diff

	if (filtered_users is None or (username in filtered_users)) and (blacklisted_users is None or not (username in blacklisted_users)):
		totalcount += diff

	if mode == "chatmessages":
		print (result.group(3))

	return {
		"type": "message",
		"time": result.group(1),
		"user": result.group(2),
		"message": result.group(3)
	}

# 12:34 <nickname>
def parseLineTimestampEmptyChat(line):
	reg = '(' + reTimestamp1 + ')\ \<(' + reNickname + ')\>'
	p = re.compile(reg)
	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "message",
		"time": result.group(1),
		"user": result.group(2),
		"message": ""
	}

def parseLogStatus(line):
	reg = '\-\-\-\ (Log\ opened|Log\ closed|Day\ changed)\ (.*)'
	p = re.compile(reg)

	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "logstatus",
		"time": result.group(1),
		"message": result.group(2)
	}

# 07:11 -!- alpha123__ is now known as alpha123
def parseRename(line):
	reg = '(' + reTimestamp1 + ')\ ' + reExclamation + '\ (' + reNickname + ')\ is now known as (' + reNickname + ')'
#	print(reg)
#	sys.exit(0)
	p = re.compile(reg)

	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "rename",
		"time": result.group(1),
		"user_old": result.group(2),
		"user_new": result.group(3)
	}

# 12:34 -!- nickname [webchat@vbo91-3-82-243-220-69.fbx.proxad.net] has joined #room-dev
# 12:34 -!- nickname [~something@h-12-34.A567.home.station.com] has quit [Signed off]
def parseLineClientStatus1(line):
	reHostname = "[a-zA-Z0-9\-\.\_]*"
	reg = '(' + reTimestamp1 + ')\ ' + reExclamation + '\ (' + reNickname + ')\ \[\~?(' + reNickname + ')\@(' + reHostname + ')\]\ (' + reMessage + ')'
	p = re.compile(reg)

	result = p.fullmatch(line)
	if result is None:
		return None

	return {
		"type": "client-message",
		"time": result.group(1),
		"user": result.group(2),
		"username": result.group(3),
		"hostname": result.group(4),
		"message": result.group(5)
	}

# 12:39 [Users #0ad]
# 12:34 [ Nickname1 ] [ Nickname2	    ] [ Nickname3]
def parseUserList(line):
	reg = '(' + reTimestamp1 + ')\ (\[(Users\ \#)?' + reNickname + '\s*\]\ ?)+'
	p = re.compile(reg)

	result = p.fullmatch(line)

	if result is None:
		return None
#	print(line)
	return {
		"type": "netstatus",
		"time": result.group(1)
	}


# 12:34 -!- Netsplit *.net <-> *.split quits: nickname1, nickname2, ..., nicknameN
# 12:34 -!- Netsplit over, joins: nickname1, nickname2, ..., nicknameN
# 12:34 -!- mode/#room-dev [+o nickname] by Q
# 04:36 -!- ServerMode/#room [+o Q] by *.quakenet.org
# 01:24 -!- Irssi: #room: Total of 32 nicks [2 ops, 0 halfops, 0 voices, 30 normal]
# 01:24 -!- Channel #room created Wed Aug  5 10:26:06 2009
# 01:24 -!- Irssi: Join to #room was synced in 7 secs
# 09:35 -!- Nickname changed the topic of #room to: topic
# 19:06 -!- Nickname was kicked from #room by nickname2 [reason]
def parseLineNetStatus(line):
	#reg = '(' + reTimestamp1 + ')\ ' + reExclamation + '\ (Netsplit|Channel\ \#|Irssi\:\ \#|mode\/\#|ServerMode\/\#)(' + reMessage + ')'
	reg = '(' + reTimestamp1 + ')\ ' + reExclamation + '\ (' + reMessage + ')'
	p = re.compile(reg)

	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "netstatus",
		"time": result.group(1),
		"message": result.group(2)
	}

# 12:34:56 * nick|away has quit (Quit: (message))
'''
def parseLineClientStatus2(line):
	reHostname = "[a-zA-Z0-9]*"
	reg = '(' + reTimestamp2 + ')\ \*\ (' + reNickname + ')\ (' + reMessage + ')'
	p = re.compile(reg)

	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "client-message",
		"time": result.group(1),
		"user": result.group(2),
		"message": result.group(3)
	}
'''

# 20:41  * Nickname does something
def parseLineChatAction(line):
	reg = '(' + reTimestamp1 + ')\ \ \*\ (' + reNickname + ')(' + reMessage + ')'
	p = re.compile(reg)
	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "chat-action",
		"time": result.group(1),
		"user": result.group(2),
		"action": result.group(3)
	}

# 03:16 !port80a.se.quakenet.org on 1 ca 1(4) ft 20(20)
# 21:09 !servercentral.il.us.quakenet.org Highest connection count: 7828 (7827 clients)
# 17:01 -N(control@services.uk.quakenet.org)- (Broadcast) message
# 16:56 -N7(control@services.de.quakenet.org)- (Broadcast) message
def parseLineBroadcast(line):
	reg = '(' + reTimestamp1 + ')\ [\!\-](' + reMessage + ')'
	p = re.compile(reg)
	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "broadcast",
		"message": result.group(1)
	}

# 12:34 * Now talking in #room
def parseLineTimestampStatus1(line):
	p = re.compile('(' + reTimestamp1 + ')\ \*\ (' + reMessage + ')')
	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "status1",
		"time": result.group(1),
		"message": result.group(2)
	}

# 12:34 *** Nickname has left #wfg
# 12:34 -L- [#wfg] Welcome to the IRC channel, http://www.website.com/
def parseLineTimestampStatus2(line):
	p = re.compile(reTimestamp1 + '\ (\*|\*\*\*|\-L\-)\ (' + reMessage + ')')
	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "status2",
		"time": result.group(1),
		"message": result.group(2)
	}

# <nickname> message
# < nickname> message
def parseLineNoTimestampChat(line):
	p = re.compile('\<(' + reNickname + ')\>\ (' + reMessage + ')')
	result = p.fullmatch(line)

	if result is None:
		return None

	global stats_chatmessages, totalcount
	username = ircnicknames.getUsername(result.group(1))
	
	diff = 1
	stats_chatmessages[username] = stats_chatmessages[username] + diff if username in stats_chatmessages else diff
	totalcount += diff

#	print (result.group(1))
#	print(stats_chatmessages)

	if mode == "chatmessages":
		print(result.group(2))

	return {
		"type": "message",
		"user": result.group(1),
		"message": result.group(2)
	}

# -L- [#wfg] foo
# *** Now talking in #wfg
# * Now talking in #room
def parseLineNoTimestampStatus(line):
	p = re.compile('(\*|\*\*\*|\-L\-)\ (' + reMessage + ')')
	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "status",
		"message": result.group(2)
	}

# Session Start: Sat Jul 02 11:21:37 2005
# Session Ident: #room
# Session Time: Sun Aug 14 00:00:00 2005
# Session Close: Sat Jul 02 11:21:37 2005
# Session Close (#wfg): Sat Nov 15 18:46:08 2003
def parseLineSession(line):
	p = re.compile('(Session Start|Session Close|Session Ident|Session Time)(\ \(.*\))?\:\ (.*)')
	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "session",
		"message": result.group(1)
	}

# (11:22:33) nickname: message
# (11:22:33) @nickname: message
# (11:22:33)  nickname: message
'''
def parseLineExtendedTimestampChat(line):
	p = re.compile("\((" + reTimestamp2 + ')\)\ (' + reNickname + ')\:\ (' + reMessage + ')')
	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "message",
		"timestamp": result.group(1),
		"user": result.group(2),
		"message": result.group(3)
	}

# (11:22:33) message
def parseLineExtendedTimestampStatus(line):
	p = re.compile("\((" + reTimestamp2 + ')\)\ (' + reMessage + ')')
	result = p.fullmatch(line)

	if result is None:
		return None

	return {
		"type": "message",
		"timestamp": result.group(1),
		"message": result.group(2)
	}
'''

def parseLineEmpty(line):
	if  line.strip():
		return None

	return {
		"type": "empty"
	}

# These work for the 2009 and 2012 set
lineParsers2009 = [
	parseLineTimestampChat,
	parseLineTimestampEmptyChat,
#	parseLineClientStatus1,
#	parseLineNetStatus,
	parseLineChatAction,
	parseLineBroadcast,
	parseLogStatus,
#	parseRename,
#	parseLineTimestampStatus1,
#	parseLineTimestampStatus2,
	parseUserList,
#	parseLineNoTimestampChat,
#	parseLineNoTimestampStatus,
#	parseLineSession,
#	parseLineEmpty
]

# These work for the 2003 set
lineParsers2003 = [
	parseLineTimestampChat,
	parseLineTimestampEmptyChat,
	parseLineClientStatus1,
	parseLineNetStatus,
	parseLineChatAction,
	parseLineBroadcast,
	parseLogStatus,
#	parseRename,
#	parseLineTimestampStatus1,
	parseLineTimestampStatus2,
#	parseUserList,
	parseLineNoTimestampChat,
	parseLineNoTimestampStatus,
	parseLineSession
#	parseLineEmpty
]

lineParsers = lineParsers2009 if fileset == "2009" else lineParsers2003

# Holds how many lines in total were parsed per format
stats_lineformat = [0] * len(lineParsers)

# Number of messages sent per user per day, or messages per user in total
stats_chatmessages = {}

def parseLine(line):

	result = None

	for i in range(len(lineParsers)):
		result = lineParsers[i](line)
		if result is not None:
			stats_lineformat[i] = stats_lineformat[i] + 1 if stats_lineformat[i] else 1
			break

	if result is None:
		pass
#		print("Failure to parse:")
#		print(line)
	else:
#		print("Result: ")
#		print(str(result))
		pass

def parseFile(file):
	#print("Opening", file)

	global stats_chatmessages, mode, totalcount

	if mode == "linesperlog":
		totalcount = 0

	if mode == "userstats_daily":
		stats_chatmessages = {}

	qbfile = open(file, "r")

	try:
		for line in qbfile:
			parseLine(line.rstrip())
	except UnicodeDecodeError as err:
		print("Error parsing", file, err)

	qbfile.close()

	if mode == "linesperlog":
		print(totalcount, "%", file)

def parseFiles(path):

	global stats_lineformat, filtered_year, filtered_dev_channel, stats_chatmessages, totalcount;
	
	last_month = None
	last_week = None

	for root, directory, files in os.walk(path):
		directory.sort()
		files.sort()
		for file in files:

			if '.log' not in file:
				continue

			# filter development channel
			if filtered_dev_channel and "#0ad.log" in file and os.path.isfile(os.path.join(root, file.replace("#0ad.log", "#0ad-dev.log"))):
				continue

			# filter year
			if filtered_year is not None and filtered_year not in file:
				continue

			# print stats per day
			'''
			stats_lineformat = [0] * len(lineParsers)
			parseFile(os.path.join(root, file))
			print(file[:10], stats_lineformat[0])
			'''

			# print stats per day
			if mode == "userstats_daily":
				print(file[:10], "", end = '')
				printUserstats()

			# print stats per month
			if last_month is None:
				last_month = file[:7]

			if last_month != file[:7]:
				#print(last_month, stats_lineformat[0])
				if mode == "userstats_monthly":
					print(last_month, "", end = '')
					printUserstats()

					stats_chatmessages = {}
					totalcount = 0;
				last_month = file[:7]
				stats_lineformat = [0] * len(lineParsers)

			parseFile(os.path.join(root, file))
