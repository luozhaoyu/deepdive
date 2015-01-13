# should be run from ChtcRun directory

filepath="~/DeepDive/downloads/"

# clean up journal name, removing commas and spaces
journal=$1
tag=$2
journal_clean=${journal//,/}
journal_clean=${journal_clean// /_}

python ../deepdive/pdf_to_dag.py "$filepath""$journal" "$journal_clean"$tag

# assume ChtcRun/shared exists and holds all common shared junk
cp -r shared "$journal_clean""$tag"

echo "Submit directories prepared! Use mkdag to create the DAGs, passing relevant runtime arguments. e.g.:"
echo ./mkdag --cmdtorun=ocr_pdf.py --parg=input.pdf --parg="--cuneiform" --parg="--tesseract" --data=$journal_clean$tag --outputdir="$journal_clean""$tag"_out --pattern=*.html --type=other                                                                                 
