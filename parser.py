#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, re, sys, getopt

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
filtered_users = [
	"elexis",
	"stan",
	"leper",
	"wraitii",
	"sanderd17",
	"Philip",
	"trompetin17",
	"historic_bruno",
	"alpha123",
	"Mythos_Ruler",
	"Itms",
	"Vladislav",
	"Imarok",
	"RedFox",
	"Josh",
	"Enrique",
	"Yves",
	"FeXoR",
	"scythetwirler",
	"fatherbushido",
	"fpre",
	"quantumstate",
	"k776",
	"niektb",
	"bb",
	"Angen",
	"Pureon",
	"Deiz",
	"radagast",
	"Freagarach",
	"feneur",
	"echotangoecho",
	"vtsj",
	"Sandarac",
	"temple",
	"mimo",
	"thamlett",
	"implodedok",
	"LordGood",
	"Gallaecio",
	"causative",
	"cc",
	"Arthur_D",
	"brian",
	"Spahbod",
	"stwf",
	"fcxSanya",
	"Jeru",
	"smiley",
	"ricotz",
	"nani",
	"fabio",
	"user1",
	"_kali",
	"s0600204",
	"asterix",
	"Dunedan",
	"Tobbi",
	"KennyLong"
];

#filtered_users = None;

filtered_users = [
	"Angen",
	"elexis",
	"fatherbushido",
	"Freagarach",
	"Itms",
	"leper",
	"Mythos_Ruler",
	"Philip",
	"sanderd17",
	"stan",
	"wraitii",
	"Vladislav"
];

# these users are ignored when counting the total number of lines posted
blacklisted_users = [
	"WildfireBot",
	"WildfireRobot"
];

def main(argv):

	parseArgs(argv)

	global fileset, root, mode
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
		printedSomething = False
		stats = [(k, stats_chatmessages[k]) for k in sorted(stats_chatmessages, key=stats_chatmessages.get, reverse=True)]
		for username, count in stats:
			if count > minimum_count and (filtered_users is None or (username in filtered_users)) and (blacklisted_users is None or not (username in blacklisted_users)):
				print(username, count)
				printedSomething = True
		if not printedSomething:
			print()
	else:
		print(totalcount, "", end = '')
		for username in filtered_users:
			if username in stats_chatmessages:
				print(stats_chatmessages[username], "", end = '')
			else:
				print(0, "", end = '')


def parseArgs(argv):
	try:
		opts, args = getopt.getopt(argv, "m", ["mode="])

	except getopt.GetoptError:
		print ('parser.py -m <mode>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-m':
			mode = arg

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

	username = getUsername(result.group(2))

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

# TODO: should be moved to a dictionary
# TODO: should verify each nick
def getUsername(txt):

	txt = txt.replace("@", "").strip()
	lower = txt.lower()

	if "wijit" in lower or "jason" in lower:
		return "Wijitmaker"

	if "ykkrosh" in lower or "philip" in lower:
		return "Philip"

	if "janwas" in lower or "jw" in lower or "wfg_jan" in lower: #TODO
		return "janwas"

	if "feneu" in lower or "erik" in lower:
		return "feneur"

	if "gee" == lower:
		return "Gee"

	if "acume" in lower:
		return "Acumen"

	if "matt" in lower:
		return "Matt"

	if "matei" in lower:
		return "matei"

	if "prefect" in lower:
		return "prefect"

	if "dax" in lower:
		return "dax"

	if "wildfirebot" in lower:
		return "WildfireBot";

	if "wildfirerobot" in lower:
		return "WildfireRobot";

	if "fire_g|" in lower or "firegiant" in lower or "fire_giant" in lower:
		return "Fire_Giant"

	if "brian" in lower:
		return "brian"

	if "dave" in lower:
		return "dave"

	if "svede" in lower:
		return "svede"

	if "cheez" in lower:
		return "CheeZy"

	if "mythos" in lower:
		return "Mythos_Ruler"

	if "seth" in lower:
		return "seth"

	if "bruno" in lower:
		return "historic_bruno"

	if "sander" in lower:
		return "sanderd17"

	if "josh" in lower:
		return "Josh"

	if "redfox" in lower:
		return "RedFox"

	if "vladislav" in lower:
		return "Vladislav"

	if "causative" in lower:
		return "causative"

	if "bb_" in lower or "bb1" in lower:
		return "bb"

	if "leper" in lower:
		return "leper"

	if "mimo" in lower:
		return "mimo"

	if "itms" in lower:
		return "Itms"

	if "markt" in lower:
		return "MarkT"

	if "fpre" in lower or "ffff" in lower or "fraizy" in lower or lower == "fg" or lower == "fff" or lower == "ff" or txt == "superelexis":
		return "fpre"

	if "fcxsanya" in lower:
		return "fcxSanya"

	if "bushido" in lower or "bushitodo" in lower or "abnegation" in lower:
		return "fatherbushido"

	if "enrique" in lower:
		return "Enrique"

	if "yves" in lower:
		return "Yves"

	if "scythetwirler" in lower or "scytheswirler" in lower or "scythewhirler" in lower:
		return "scythetwirler"

	if "stan" in lower:
		return "stan"

	if "fabio" in lower:
		return "fabio"

	if "wraitii" in lower:
		return "wraitii"

	if "fexor" in lower:
		return "FeXoR"

	if "smiley" in lower:
		return "smiley"

	if "elexis" in lower:
		return "elexis"

	if "cc__" in lower or "cc_laptop" in lower or lower == "cc_" or "cc_1" == lower:
		return "cc"

	if "angen" in lower and not "dvangennip" in lower:
		return "Angen"

	if "k776" in lower:
		return "k776"

	if "trompeti" in lower or "tromeptin17" in lower:
		return "trompetin17"

	if "dunedan" in lower:
		return "Dunedan"

	if "temple" in lower:
		return "temple"

	if "telaviv" not in lower and "aviv" in lower or "jeru" in lower:
		return "Jeru"

	if "niektb" in lower:
		return "niektb"

	if "imarok" in lower:
		return "Imarok"

	if "gallaecio" in lower:
		return "Gallaecio"

	if "kimball" in lower:
		return "Kimball"

	if "arthur_d" in lower:
		return "Arthur_D"

	if "grugnas" in lower:
		return "Grugnas"

	if "theshadow" in lower:
		return "theShadow"

	if "nani0" in lower:
		return "nani"

	if "kennylong" in lower or "chakakhan" in lower:
		return "KennyLong"

	if "thamlett" in lower:
		return "thamlett"

	if "alpha123" in lower:
		return "alpha123"

	if txt == "GK-Daniel" or txt == "GKDaniel" or txt == "GK_Daniel":
		return "alpha123"

	if "safa" in lower:
		return "Safa_[A_boy]"

	if "eihrul" in lower:
		return "eihrul"

	if "kali" in lower:
		return "_kali"

	if "sighvatr" in lower:
		return "Sighvatr"

	if "igor" in lower:
		return "igor"

	if "agentx" in lower:
		return "agentx"

	if "badmadblacksad" in lower:
		return "Badmadblacksad"

	if "bichtiades" in lower:
		return "Bichtiades"

	if "dalerank" in lower:
		return "Dalerank"

	if "erraunt" in lower:
		return "erraunt"

	if "evans" in lower:
		return "evans"

	if txt == "Gusse":
		return "Gussebb"

	if txt == "HenryJia":
		return "Henry_Jia_T60"

	if txt == "Jagst3r21_":
		return "Jagst3r21"

	if "infyquest" in lower:
		return "infyquest"

	if "mfmachado" in lower:
		return "mfmachado"

	if "nylki" in lower:
		return "nylki"

	if "quantumstate" in lower:
		return "quantumstate"

	if "rjs23" in lower:
		return "rjs23"

	if "santa_" in lower:
		return "santa_"

	if "spahbod" in lower:
		return "Spahbod"

	if "stwf" in lower:
		return "stwf"

	if "trajan34" in lower:
		return "trajan34"

	if "wacko" in lower:
		return "wacko"

	if "xeramon" in lower:
		return "Xeramon"

	if "zaggy" in lower:
		return "Zaggy1024"

	if "amish" in lower:
		return "amish"

	if "alex|d-guy" in lower:
		return "alex|D-Guy"

	if "cygal" in lower:
		return "cygal"

	if txt == "rada"  or txt == "radagast" or txt == "rada_":
		return "radagast"

	if "skhorn" in lower:
		return "skhorn"

	if "keenehteek" in lower:
		return "keenehteek"

	# not sure if this is the same as GK-Daniel
	if txt == "Daniel_":
		return "Daniel_"

	if txt == "prod_":
		return "prod"

	if txt == "ffm_":
		return "ffm"

	#mark____

	return txt.strip()

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
	username = getUsername(result.group(1))
	
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

	if mode == "userstats_daily":
		print(file)
		printUserstats()

	elif mode == "linesperlog":
		print(totalcount, "%", file)

def parseFiles(path):
	global stats_lineformat, filtered_year, filtered_dev_channel, stats_chatmessages, totalcount;
	last_month = None
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

			# print stats per month
			if last_month is None:
				last_month = file[:7]

			if last_month != file[:7]:
				#print(last_month, stats_lineformat[0])
				if mode == "userstats_monthly":
					print(last_month, "", end = '')
					printUserstats()
					print()

					stats_chatmessages = {}
					totalcount = 0;
				last_month = file[:7]
				stats_lineformat = [0] * len(lineParsers)

			parseFile(os.path.join(root, file))

if __name__ == "__main__":
	main(sys.argv[1:])
