# should be run from ChtcRun directory
# needs to: 
    # create submit dir
    # set up proper shared/ stuff
    # loop over _out dirs, copying tess*.hocr over
    # run mkdag

# clean up journal name, removing commas and spaces
journal=$1
journal_clean=${journal//,/}
journal_clean=${journal_clean// /_}
journal_out="$journal_clean"_out
journal_new="$journal_clean"_NLP

for job in "$journal_out"/job*281/;
do
    echo $job
    if ls $job/tess*hocr 1> /dev/null 2>&1; then
        mkdir -p $journal_new${job/$journal_out/}
        ln -s `pwd`/$job/tess*hocr $journal_new${job/$journal_out/}
        # would this work as a symbolic link instead?
    fi
done

# assume ChtcRun/NLPshared exists and holds all common shared junk
cp -r NLPshared $journal_new
mv $journal_new/NLPshared $journal_new/shared
./mkdag --cmdtorun=do.sh --data=$journal_new --outputdir="$journal_new"_out_test --pattern=SUCCEED.txt --type=other                                                                                 
