import sys, ircparser

# These users have been around significantly long enough to be counted as part of the relevant community
'''
filtered_users = [
    "elexis",
    "Stan",
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
'''

# More strict list
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
    "Stan",
    "wraitii",
    "Vladislav"
];

blacklisted_users = [
    "WildfireBot",
    "WildfireRobot"
];

ircparser.parse(filtered_users, blacklisted_users)

