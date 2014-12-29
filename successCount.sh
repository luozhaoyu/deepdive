# Run from submit dir.
# Looks for success flags in the [journal]_out/[jobid]/RESULT files,
# writing the journal name and total successes for each

rm successCount.csv
total=0
for f in *_out/;
do
    fspace=${f//_/ }
    fclean=${fspace// out/}
    fclean=${fclean//\//}
    cat "$f"*/RESULT | grep 0 | wc -l | xargs echo $fclean",">> successCount.csv
done
