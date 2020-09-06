import json
import plotter

out_directory = "charts/"
postfix = ".png"

color_project = "black"
color_user = "darkred"

figsize = [25, 15]
dpi = 100

with open('data/git_month.txt') as f:
    commitlines = f.readlines()
(commit_usernames, commit_values) = plotter.parse_commit_stats(commitlines, 2012)

with open('data/irc_month.txt') as f:
    chatlines = f.readlines()
(chat_usernames, chat_values) = plotter.parse_ircstats(chatlines)

with open('input/events.json') as json_file:
    events = json.load(json_file)

def filename(print_chat, print_commit, username):
    return out_directory + username + "_" + ("both" if print_chat and print_commit else "commit" if print_commit else "chat") + postfix

for (print_chat, print_commit) in [(True, True)]:#, (True, False), (False, True)]:
    # Plot one graph per user:
    if True:
        for username in chat_usernames:
            if username != "Total":
                plotter.plot_graph(
                    filename(print_chat, print_commit, username),
                    ["Total", username],
                    commit_values,
                    chat_values,
                    #trac_values,
                    events,
                    print_chat,
                    print_commit,
                    color_project,
                    color_user,
                    figsize,
                    dpi)

    # Plot one graph for all userss
    plotter.plot_graph(
        filename(print_chat, print_commit, "Total"),
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
        #trac_values,
        events,
        print_chat,
        print_commit,
        color_project,
        color_user,
        figsize,
        dpi)
