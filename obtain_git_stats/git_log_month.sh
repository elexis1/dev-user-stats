cd input/git;

first_year=2003
end_year=`date +'%Y'`
branch="wfg/master"
ignoredauthors="autobuild\|na-Itms"

for year in $(seq $first_year $end_year); do
	for month in $(seq 1 12); do
		start_day="$year-$month-01"
		start=$(date --date="$start_day" +"%Y-%m")
		end=$(date --date="$start_day +1 month" +"%Y-%m")
		echo $start
		git shortlog --no-merges --invert-grep --author="$ignoredauthors"  -sn "$branch" --after="$start-01" --before="$end-01"
	done
done

