#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Delete those invalid pdf under certain directory
Attributes:

Google Python Style Guide:
    http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
"""
__copyright__ = "Zhaoyu Luo"

import os

from PyPDF2 import PdfFileReader


def main():
    from sys import argv
    folder = argv[1]
    for f in os.listdir(folder):
        filepath = os.path.join(folder, f)
        try:
            input = PdfFileReader(open(filepath, 'rb'))
        except Exception:
            print "Broken\t%s" % filepath
            if len(argv) > 1 and argv[2] == 'delete':
                os.remove(filepath)
                print "Deleted\t%s" % filepath


if __name__ == '__main__':
    main()
