#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Brief Summary
Attributes:

Google Python Style Guide:
    http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
"""
__copyright__ = "Zhaoyu Luo"

import os
import pickle
import shutil


def organize_htcondor_jobs(origin_input_folder,
        htcondor_input_folder, htcondor_output_folder, output_folder):
    """Reorganize the processed ocr results into tree structure

    Args:
        folder paths

    Returns:
        True
    """
    origin_input_folder = os.path.abspath(origin_input_folder)
    input_info = None
    for f in os.listdir(htcondor_input_folder):
        if f.endswith('pickle'):
            with open(os.path.join(htcondor_input_folder, f), 'rb') as pf:
                input_info = pickle.load(pf)

    if not input_info:
        raise Exception("There is no pickle file in %s" % htcondor_input_folder)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for job_name in os.listdir(htcondor_output_folder):
        job_dir_path = os.path.join(htcondor_output_folder, job_name)
        if job_name in input_info:
            # base on the original input folder path, cut the prefix
            new_organized_path = os.path.join(output_folder,
                os.path.abspath(input_info[job_name])\
                    [len(origin_input_folder)+1:])
            if os.path.exists(new_organized_path):
                print "Warning: %s existed, skip copy from %s to %s"\
                    % (new_organized_path, job_dir_path, new_organized_path)
                continue
            else:
                os.makedirs(new_organized_path)

            for f in os.listdir(job_dir_path):
                if f != "out.txt" and \
                    (f.endswith('.txt') or f.endswith('.html') \
                    or f.endswith('.pdf') or f.endswith('.hocr') ):
                    shutil.copy(
                        os.path.join(htcondor_output_folder, job_name, f),
                        new_organized_path)
        else:
            if os.path.isdir(job_dir_path):
                raise Exception("Please check %s,"
                    "no information found in pickle"
                    % job_name)


def main():
    """Main function only in command line"""
    from sys import argv
    if len(argv) != 5:
        print "Usage: python organize_htcondor_jobs"\
            "ORIGIN_FOLDER FOLDER_HOLDING_PICKLE"\
            "FOLDER_HOLDING_OCR_RESULT OUTPUT"
        print "e.g. python organize_htcondor_jobs.py "\
            "/home/iaross/merlin/toxic/uniroyal/ "\
            "/home/iaross/merlin_001/test_run/ChtcRun/uniroyal "\
            "/home/iaross/merlin_001/test_run/ChtcRun/uniroyal_out/ myout"
        return False
    organize_htcondor_jobs(argv[1], argv[2], argv[3], argv[4])



if __name__ == '__main__':
    main()
