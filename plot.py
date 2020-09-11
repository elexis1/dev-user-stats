import json
import os
import plot.plot_commit
import plot.plot_irc
import plot.plot_trac
import plot.plotter

data_directory = "data/"
out_directory = "charts/"
postfix = ".png"

color_event_project = "black"
color_event_user = "darkred"
color_commit_total = "green"
color_commit_user = "red"

trac_keywords = ["combined"] # rfc/review distinction too noisy
trac_actions = ["added", "removed"]
print_events = True

figsize = [25, 15]
dpi = 100
min_year = 2009

with open(data_directory + "git_month.txt") as f:
    commitlines = f.readlines()
(commit_usernames, commit_values) = plot.plot_commit.parse_commit_stats(commitlines, min_year)

with open(data_directory + "irc_month.txt") as f:
    chatlines = f.readlines()
(chat_usernames, chat_values) = plot.plot_irc.parse_irc_stats(chatlines)

trac_values = {
    "actions": plot.plot_trac.parse_trac_actions(data_directory, min_year, ["review", "rfc"], ["added", "removed"]),
    "open": plot.plot_trac.parse_trac_open(data_directory, min_year, ["review", "rfc"])
}

plot.plot_trac.print_trac_userstats(trac_values["actions"], ["combined"], ["added", "removed"])

with open('input/events.json') as json_file:
    events = json.load(json_file)

def filename(print_chat, print_commit, print_trac, username):
    return out_directory + \
        username + \
        ("_commit" if print_commit else "") + \
        ("_chat" if print_chat else "") + \
        ("_trac" if print_trac else "") + \
        postfix


try:
    os.mkdir(out_directory)
except:
    pass

chat_usernames = ["historic_bruno"]

for (print_chat, print_commit, print_trac) in [(True, True, True)]:#, (True, False), (False, True)]:
    # Plot one graph per user:
    if True:
        for username in chat_usernames:
            if username != "Total":
                plot.plotter.plot_graph(
                    filename(print_chat, print_commit, print_trac, username),
                    ["Total", username],
                    commit_values,
                    chat_values,
                    trac_values,
                    events,
                    print_chat,
                    print_commit,
                    print_trac and False, # trac open
                    print_trac, # trac actions
                    print_events,
                    trac_keywords,
                    trac_actions,
                    color_event_project,
                    color_event_user,
                    color_commit_user,
                    color_commit_total,
                    figsize,
                    dpi)

    # Plot one graph for all userss
    print_chat = False
    print_commit = False
    print_trac = True
    plot.plotter.plot_graph(
        filename(print_chat, print_commit, print_trac, "Total"),
        [
            "Total",
            #"elexis",
            #"leper",
            #"wraitii",
            #"Stan",
            #"Itms",
        ],
        commit_values,
        chat_values,
        trac_values,
        events,
        print_chat,
        print_commit,
        print_trac,
        True,
        print_events,
        trac_keywords,
        trac_actions,
        color_event_project,
        color_event_user,
        color_commit_user,
        color_commit_total,
        figsize,
        dpi)
