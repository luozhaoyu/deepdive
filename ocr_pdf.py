#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    ocr_pdf.py
    ~~~~~~~~~~~~~~

    A brief description goes here.
"""
import subprocess
import os
import shutil

def call(cmd, check=True, stdout=None, stderr=None):
    """
        Args:
            check: check return code or not
    """
    if check:
        return subprocess.check_call(cmd, stdout=stdout, stderr=stderr, shell=True)
    else:
        return subprocess.call(cmd, stdout=stdout, stderr=stderr, shell=True)


def k2pdfopt(pdf_file, output_file, func=call):
    """convert multi-column PDF into single column

    K2pdfopt (Kindle 2 PDF Optimizer) is a stand-alone program which optimizes the format of PDF (or DJVU) files for viewing on small (e.g. 6-inch) mobile reader and smartphone screens such as the Kindle's.
    The output from k2pdfopt is a new (optimized) PDF file.
    http://www.willus.com/k2pdfopt/

    Args:
        output_file: this is a required parameter, because k2pdfopt always return 0

    Returns:
        0: WARNING, k2pdfopt will always return 0, judge its succeed by looking at the output_file
    """
    try:
        os.remove(output_file)
    except OSError as e:
        if e.errno != 2:
            raise e
    cmd = "./k2pdfopt -ui- -x -w 2160 -h 3840 -odpi 300 %s -o %s" % (pdf_file, output_file)
    return func(cmd)


def pdf_to_png(pdf_file, tmp_folder=None, func=call):
    if tmp_folder:
        cmd = "./codes/convert/cde-exec 'gs' -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -r300 -sOutputFile=%s/page-%%d.png %s"\
            % (tmp_folder, pdf_file)
    else:
        cmd = "./codes/convert/cde-exec 'gs' -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -r300 -sOutputFile=page-%%d.png %s" % pdf_file
    return func(cmd)


def pdf_to_bmp(pdf_file, tmp_folder=None, func=call):
    if tmp_folder:
        cmd = "./codes/convert/cde-exec 'gs' -SDEVICE=bmpmono -r300x300 -sOutputFile=%s/cuneiform-page-%%04d.bmp -dNOPAUSE -dBATCH -- %s"\
                % (tmp_folder, pdf_file)
    else:
        cmd = "./codes/convert/cde-exec 'gs' -SDEVICE=bmpmono -r300x300 -sOutputFile=cuneiform-page-%%04d.bmp -dNOPAUSE -dBATCH -- %s" % pdf_file
    return func(cmd)


def tesseract(png_folder_path):
    for i in os.listdir(os.path.abspath(png_folder_path)):
        if i.endswith('.png'):
            print i


class OcrPdf(object):
    def __init__(self, pdf_path, stdout_filepath, stderr_filepath):
        try:
            self.stdout = open(stdout_filepath, 'a')
            self.stderr = open(stderr_filepath, 'a')
            self.pdf_path = pdf_path
        except IOError as e:
            print "ERROR\tInvalid filepath %s, %s" % (stdout_filepath, stderr_filepath)
            if self.stdout:
                self.stdout.close()
            if self.stderr:
                self.stderr.close()
            raise e

        shutil.rmtree('tmp', True)
        try:
            os.mkdir('tmp')
        except OSError as e:
            print "ERROR\tCreate tmp folder"
            raise e

    def __del__(self):
        shutil.rmtree('tmp', True)

    def call(self, cmd, check=True):
        return call(cmd, check=check, stdout=self.stdout, stderr=self.stderr)

    def do(self):
        output_file = "k2_pdf_%s" % self.pdf_path
        print k2pdfopt(self.pdf_path, output_file, func=self.call)
        print pdf_to_png(output_file, tmp_folder='tmp', func=self.call)
        print pdf_to_bmp(output_file, tmp_folder='tmp', func=self.call)
        print tesseract('tmp')


def main(argv):
    o = OcrPdf(argv[1], 'out.txt', 'out.txt')
    o.do()


if __name__ == '__main__':
    import sys
    main(sys.argv)
