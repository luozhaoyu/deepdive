# should be run from the [tagName]/deepdive directory
# will create the [tagName]/ChtcRun and prep it for condor job submission

cd ..

# grab ChtcRun stuff
wget http://chtc.cs.wisc.edu/downloads/ChtcRun.tar.gz
tar xzf ChtcRun.tar.gz

cd ChtcRun

# symbolic links to create scripts
ln -s ../deepdive/createJobs.sh .
ln -s ../deepdive/createTessNLPJobs.sh .

# if shared, nlpShared exist in deepdive, cp them here
if [ -d "../shared/" ]; then
    cp -r ../shared/ .
    if [ -e "shared/URLS" ]; then
        while read p; do
            sha1sum "/squid"$p >> sha1sums
        done <shared/URLS
    fi
fi

if [ -d "../NLPshared/" ]; then
    cp -r ../NLPshared/ .
    if [ -e "NLPshared/URLS" ]; then
        while read p; do
            sha1sum "/squid"$p >> sha1sums
        done < NLPshared/URLS
    fi
fi

echo "Ready to go! Head over to the ChtcRun directory and use the createJobs.sh (or similar) scripts to generate jobs."
