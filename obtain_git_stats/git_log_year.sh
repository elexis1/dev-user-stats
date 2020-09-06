cd input/git;

first_year=2003
end_year=`date +'%Y'`

for year in $(seq $first_year $end_year);
do
	year_next=$(($year+1))
	echo "$year"
	git shortlog --invert-grep --author=autobuild --no-merges  -sn wfg/master --after="$year-01-01" --before="$year_next-01-01"
done
