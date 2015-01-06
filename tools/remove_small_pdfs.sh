#!/bin/sh
find /scratch/pdfs/ -type f -size -4506c
echo "Above files are being removed..."
find /scratch/pdfs/ -type f -size -4506c| xargs rm -f
