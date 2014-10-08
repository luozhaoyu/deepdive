#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    pdf_to_dag.py
    ~~~~~~~~~~~~~~

    list files within directories
"""
import os
import pickle

def get_job_directory(input_path, output_path):
    """
        Returns:
            {}, contains original file information
    """
    info = {}
    count = 0
    for root, dirs, files in os.walk(input_path):
        fileinfos = {}
        for f in files:
            suffix = f.split('.')[-1].lower()
            if suffix == "pdf" or suffix.startswith("tif"):
                filepath = os.path.realpath(os.path.join(root, f))
                count += 1

                new_job_folder_name = "job%03d" % count
                new_job_folder_path = os.path.join(output_path, new_job_folder_name)
                try:
                    os.makedirs(new_job_folder_path)
                except OSError:
                    # it is acceptable to encounter makedir error before create symbol link
                    pass

                link_name = os.path.join(new_job_folder_path, "input.%s" % suffix)
                try:
                    os.symlink(filepath, link_name)
                    info[new_job_folder_name] = filepath
                except os.error as e:
                    print "Fail to create symbol link %s towards %s" % (link_name, filepath)
                    raise e
    return info


def main(argv):
    if len(argv) == 3 and os.path.isdir(argv[1]) and not os.path.exists(argv[2]):
        info = get_job_directory(argv[1], argv[2])
        try:
            with open(os.path.join(argv[2], "filepath_mapping.pickle"), 'wb') as f:
                pickle.dump(info, f)
        except pickle.PickleError as e:
            print "WARNING: Fail to serialize original filepath information"
            raise e
        else:
            print "Succeed!"
    else:
        print "Please indicate existed input path and non-existed output directory!"
        sys.exit(1)


if __name__ == '__main__':
    import sys
    main(sys.argv)
