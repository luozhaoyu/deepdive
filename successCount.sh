#!/bin/sh

# Run from submit dir.
# Looks for success flags in the [journal]_out/[jobid]/RESULT files,
# writing the journal name and total successes for each

pushd /home/iaross/elsevier_002/ChtcRun/

tag=$1

rm successCount$tag.csv
total=0
for f in *_out$tag/;
do
    fclean=${f//$tag/}
    fspace=${fclean//_/ }
    fclean=${fspace// out/}
    fclean=${fclean//\//}
    cat "$f"*/RESULT | grep 0 | wc -l | xargs echo $fclean",">> successCount$tag.csv
done

popd
