#!/bin/sh

input="input/git/.git/"
output="data"
branch="wfg/master"
excluded_authors="autobuild\|na-Itms"

first_year=$(git --git-dir "$input" log --pretty=format:"%cd" --date=iso --date=format:"%Y" | sort | head -n 1)
last_year=$(git --git-dir "$input" log --pretty=format:"%cd" --date=iso --date=format:"%Y" | sort -r | head -n 1)

filter_args="--no-merges --invert-grep --author=$excluded_authors"

# All commits, date + author, ordered by date:
out="$output/git_day.txt"
echo "Printing all commits to $out"
git --git-dir "$input" log "$branch" $filter_args --format="%as %H %an" | sort -r > "$out"

# Commits summarized by current_year:
out="$output/git_year.txt"
rm -f "$out"
echo "Printing summaries to $out"
for current_year in $(seq "$first_year" "$last_year");
do
    next_year=$((current_year+1))
    echo "$current_year" >> "$out"
    git --git-dir "$input" shortlog "$branch" $filter_args --summary --numbered --after="$current_year-01-01" --before="$next_year-01-01" >> "$out"
done

# Commits summarized by month:
out="$output/git_month.txt"
rm -f "$out"
echo "Printing summaries to $out"
for current_year in $(seq "$first_year" "$last_year"); do
    for month in $(seq -w 1 12); do
        start_day="$current_year-$month-01"
        start_month=$(date --date="$start_day" +"%Y-%m")
        end_month=$(date --date="$start_day +1 month" +"%Y-%m")
        echo "$start_month" >> "$out"
        git --git-dir "$input" shortlog "$branch" $filter_args --summary --numbered --after="$start_month-01" --before="$end_month-01" >> "$out"
    done
done
