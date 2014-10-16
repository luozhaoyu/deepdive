#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    ocr_pdf.py
    ~~~~~~~~~~~~~~

    A brief description goes here.
"""
import subprocess

def call(cmd, check=True, stdout=None, stderr=None):
    """
        Args:
            check: check return code or not
    """
    if check:
        return subprocess.check_call(cmd, stdout=stdout, stderr=stderr, shell=True)
    else:
        return subprocess.call(cmd, stdout=stdout, stderr=stderr, shell=True)


def k2pdfopt(pdf_file, output_file):
    """
    Args:
        output_file: this is a required parameter, because k2pdfopt always return 0

    Returns:
        0: WARNING, k2pdfopt will always return 0, judge its succeed by looking at the output_file
    """
    cmd = "./k2pdfopt -ui- -x -w 2160 -h 3840 -odpi 300 %s -o %s" % (pdf_file, output_file)
    return call(cmd)


def pdf_to_page(pdf_file):
    cmd = "./codes/convert/cde-exec 'gs' -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -r300 -sOutputFile=page-%%d.png %s" % pdf_file
    call(cmd)
    cmd = "./codes/convert/cde-exec 'gs' -SDEVICE=bmpmono -r300x300 -sOutputFile=cuneiform-page-%%04d.bmp -dNOPAUSE -dBATCH -- %s" % pdf_file
    return call(cmd)


class OcrPdf(object):
    def __init__(self, stdout_filepath, stderr_filepath):
        try:
            self.stdout = open(stdout_filepath, 'a')
            self.stderr = open(stderr_filepath, 'a')
        except IOError as e:
            print "ERROR\tInvalid filepath %s, %s" % (stdout_filepath, stderr_filepath)
            if self.stdout:
                self.stdout.close()
            if self.stderr:
                self.stderr.close()
            raise e

    def call(self, cmd, check=True):
        return call(cmd, check=check, stdout=self.stdout, stderr=self.stderr)


def main(argv):
    output_file = "k2_pdf_%s" % argv[1]
    print k2pdfopt(argv[1], output_file)
    print pdf_to_page(output_file)


if __name__ == '__main__':
    import sys
    main(sys.argv)
