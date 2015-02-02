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
import glob
import argparse

def call(cmd, check=True, stdout=None, stderr=None):
    """
    Args:
        check: check return code or not
    """
    if check:
        return subprocess.check_call(cmd, stdout=stdout, stderr=stderr, shell=True)
    else:
        return subprocess.call(cmd, stdout=stdout, stderr=stderr, shell=True)


def unzip(zip_file, func=call):
    cmd = "unzip -o '%s'" % zip_file
    try:
        return func(cmd)
    except subprocess.CalledProcessError as e:
        if e.returncode != 2:
            raise e


def cp(wild_pathname, dst):
    """Unix-like file copy"""
    for src in glob.glob(wild_pathname):
        if os.path.isdir(dst):
            shutil.copy(src, os.path.join(dst, os.path.basename(src)))
        else:
            shutil.copy(src, dst)
    return True


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
    cmd = "./k2pdfopt -ui- -x -w 2160 -h 3840 -odpi 300 '%s' -o '%s'" % (pdf_file, output_file)
    return func(cmd)


def pdf_to_png(pdf_file, tmp_folder=None, func=call):
    if tmp_folder:
        cmd = "./codes/convert/cde-exec 'gs' -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -r600 -sOutputFile='%s/page-%%d.png' '%s'"\
            % (tmp_folder, pdf_file)
    else:
        cmd = "./codes/convert/cde-exec 'gs' -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -r600 -sOutputFile=page-%%d.png '%s'" % pdf_file
    return func(cmd)


def pdf_to_bmp(pdf_file, tmp_folder=None, func=call):
    if tmp_folder:
        cmd = "./codes/convert/cde-exec 'gs' -SDEVICE=bmpmono -r600x600 -sOutputFile='%s/cuneiform-page-%%04d.bmp' -dNOPAUSE -dBATCH -- '%s'"\
                % (tmp_folder, pdf_file)
    else:
        cmd = "./codes/convert/cde-exec 'gs' -SDEVICE=bmpmono -r600x600 -sOutputFile='cuneiform-page-%%04d.bmp' -dNOPAUSE -dBATCH -- '%s'" % pdf_file
    return func(cmd)


def tesseract(png_folder_path, output_folder_path=None, func=call):
    """
    Returns:
        0, always return 0
    """
    png_folder_path = os.path.abspath(png_folder_path)
    if not output_folder_path:
        output_folder_path = png_folder_path
    for i in os.listdir(png_folder_path):
        if i.endswith('.png'):
            png_path = os.path.join(png_folder_path, i)
            ppm_filename = "%s.ppm" % png_path
            ppm_filename = ppm_filename.replace(".png","")
            hocr_filename = os.path.join(output_folder_path, "%s.hocr" % i.replace(".png",""))
            cmd = "./codes/convert/cde-exec 'convert' -density 750 '%s' '%s'" % (png_path, ppm_filename)
            func(cmd)
            cmd = "./codes/tesseract/cde-exec 'tesseract' '%s' '%s' hocr" % (ppm_filename, hocr_filename)
            func(cmd)
            cmd = "rm -f '%s'" % (ppm_filename)
            func(cmd)
    return 0


def cuneiform(bmp_folder_path, output_folder_path=None, func=call):
    """
    Returns:
        0, always return 0
    """
    bmp_folder_path = os.path.abspath(bmp_folder_path)
    if not output_folder_path:
        output_folder_path = bmp_folder_path
    for i in os.listdir(bmp_folder_path):
        if i.endswith('.bmp'):
            cmd = "./cde-package/cde-exec '/scratch.1/pdf2xml/cuneiform/bin/cuneiform' -f hocr -o '%s.html' '%s'"\
                % (os.path.join(output_folder_path, i), os.path.join(bmp_folder_path,i))
            func(cmd)
    return 0


def tiff_to_html(tiff_path, output_folder_path=None, func=call):
    output_folder_path = os.path.abspath(output_folder_path) if output_folder_path else os.path.abspath('.')
    hocr_path = os.path.join(output_folder_path, os.path.basename(tiff_path))
    cmd = "./codes/tesseract/cde-exec 'tesseract' '%s' '%s.hocr' hocr" % (tiff_path, hocr_path)
    return func(cmd)


class OcrPdf(object):
    def __init__(self, pdf_path, stdout_filepath, stderr_filepath,
            output_folder_path=None, cuneiform=True, tesseract=True, k2pdf = False):
        try:
            self.stdout = open(stdout_filepath, 'a')
            self.stderr = open(stderr_filepath, 'a')
            self.pdf_path = pdf_path
            self.k2pdf = k2pdf
            self.cuneiform = cuneiform
            self.tesseract = tesseract
            self.output_folder_path = output_folder_path
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

        if self.output_folder_path and not os.path.isdir(self.output_folder_path):
            try:
                os.mkdir(self.output_folder_path)
            except OSError as e:
                print "ERROR\tCreate output folder"
                raise e

    def __del__(self):
        shutil.rmtree('tmp', True)

    def call(self, cmd, check=True):
        return call(cmd, check=check, stdout=self.stdout, stderr=self.stderr)

    def do(self):
        # Usage of ocr2 and cuneiform will depend on desired runtime options.
        if self.k2pdf:
            output_file = "k2_pdf_%s" % self.pdf_path
            print k2pdfopt(self.pdf_path, output_file, func=self.call)
        else:
            output_file = self.pdf_path
        unzip("ocr2.zip", func=self.call)
        unzip("cuneiform.zip", func=self.call)
        if self.tesseract:
            print pdf_to_png(output_file, tmp_folder='tmp', func=self.call)
            print tesseract('tmp', self.output_folder_path, self.call)
        if self.cuneiform:
            print pdf_to_bmp(output_file, tmp_folder='tmp', func=self.call)
            print cuneiform('tmp', self.output_folder_path, self.call)

    def tiffs_to_htmls(self, tiff_folder_path):
        """
        Returns:
            True or the file failed to be converted
        """
        for i in os.listdir(tiff_folder_path):
            if i.endswith('.tif') or i.endswith('.tiff'):
                tiff_path = os.path.join(tiff_folder_path, i)
                if tiff_to_html(tiff_path, self.output_folder_path, self.call):
                    return tiff_path
        return True


def main(args):
    o = OcrPdf(args.file, 'out.txt', 'out.txt', './',args.cuneiform,args.tesseract,args.k2pdf)
    o.do()
#    o.tiffs_to_htmls(argv[1])


def detect_layout_fonts(pdf_file, output_folder, enable_tesseract, enable_k2pdf):
    import old_cuneiform_arcane

    o = OcrPdf(pdf_file, 'out.txt', 'out.txt', output_folder,
            True, enable_tesseract, enable_k2pdf)
    o.do()
    try:
        shutil.rmtree('tmp', True)
        os.mkdir('tmp')
        cp(os.path.join(output_folder, "cune*html"), 'tmp')
        old_cuneiform_arcane.parse_cunneiform_results_and_extract_layout_font_information('tmp')
        cp("tmp/*", output_folder)
    except:
        raise
    finally:
        shutil.rmtree('tmp', True)
        for src in glob.glob(os.path.join(output_folder, "cuneiform-page-*")):
            if os.path.isdir(src):
                shutil.rmtree(src, True)
            else:
                os.remove(src)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('file', type=str, default="input.pdf", help='Filename to process')
    parser.add_argument('--output-folder', type=str, default="./", help='output folder')
    parser.add_argument('--cuneiform', dest='cuneiform', action='store_true', help='Run Cuneiform OCR?')
    parser.add_argument('--no-cuneiform', dest='cuneiform', action='store_false', help='Run Cuneiform OCR?')
    parser.add_argument('--tesseract', dest='tesseract', action='store_true', help='Run Tesseract OCR?')
    parser.add_argument('--no-tesseract', dest='tesseract', action='store_false', help='Run Tesseract OCR?')
    parser.add_argument('--k2pdf', type=bool, required=False, default=False, help='Run k2pdf step?')
    exclusives = parser.add_mutually_exclusive_group()
    exclusives.add_argument('--fonttype', action='store_true', help='Run fonttype')

    args = parser.parse_args()
    if args.fonttype:
        detect_layout_fonts(args.file, args.output_folder,
            args.tesseract, args.k2pdf)
    else:
        main(args)
