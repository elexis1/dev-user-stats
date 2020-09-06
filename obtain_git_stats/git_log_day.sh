cd input/git;

# With commit hash and time:
# git log wfg/master --format="%aI %an %H"  | grep -v autobuild

# Only date + author
git log wfg/master --no-merges --invert-grep --author="autobuild\|na-Itms"  --format="%as %an"
