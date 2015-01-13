deepdive
========

init.sh
-------
Use the init.sh script to quickly set up a condor-ready submission area.
To use,
    
    mkdir job_submission
    cd job_submission
    git clone https://github.com/iross/deepdive
    # CREATE shared/ folder that contains URLS, executable
    cd deepdive
    sh init.sh

It will create a job_submission/ChtcRun with additional job creation scripts in place.


OCR
---

### Dealing with different file types
Currently, we made these basic assumptions when dealing with different files

* PDF: one article == one PDF, which has multiple pages
* TIFF: one article == one folder, which contains multiple TIFF files, one TIFF == one page

### Reference
* [Tesseract] (http://tesseract-ocr.googlecode.com/svn/trunk/doc/tesseract.1.html)

http://tfischernet.wordpress.com/2008/11/26/searchable-pdfs-with-linux/

### Known Issues
#### Let Cuneiform accept TIFF as its input
You have to compile cuneiform with ImageMagick++

The simplest solution is `apt-get install libmagick++-dev libmagick++1`
Otherwiese you should download ImageMagick and compile it firstly

There is a bug that cmake could not find ImageMagick after the compilation and
installation. (Assuming compile it with `./configure --prefix=$HOME/local`)
One trick hack is to violently modify `$vim cuneiform-linux-1.1.0/builddir/CMakeCache.txt`

    //Path to the ImageMagick include dir.
    ImageMagick_Magick++_INCLUDE_DIR:PATH=/u/z/h/zhaoyu/local/include/ImageMagick-6/

    //Path to the ImageMagick Magick++ library.
    ImageMagick_Magick++_LIBRARY:FILEPATH=/u/z/h/zhaoyu/local/lib/libMagick++-6.Q16.so

USGS
----
* If the target web page does not contain any files end with .pdf, we simply abort this task which would simplify our work
* If the target web page is a HTML rather than a PDF, we ignore

### Requirements
* beautifulsoup4 is a must
* pypdf2 is for checking the PDF integrity

tools
-----
This folder contains some convenient scripts which do not belong to deep-dive
