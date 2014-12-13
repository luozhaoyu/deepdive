#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    crawler.py
    ~~~~~~~~~~~~~~

    A brief description goes here.
"""
import csv
import urllib2
import urllib
import re
import os
import logging
import logging.handlers

import bs4


def create_logger(filename, logger_name=None):
    logger = logging.getLogger(logger_name or filename)
    fmt='[%(asctime)s] %(levelname)s %(message)s'
    datefmt="%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    handler = logging.handlers.RotatingFileHandler(filename, maxBytes=1024 * 1024 * 1024, backupCount=10)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


log = create_logger('crawl.log')


def retrieve(url, sbid, output_folder):
    """Download the PDF or search for the webpage for any PDF link
    Args:
        url, assuming the input url is valid
    """
    def _urlretrieve(url, filename, sbid, retry=3):
        if os.path.exists(filename):
            log.warn("%s\tDUPLICATED" % url)
            return None

        for i in range(retry):
            try:
                urllib.urlretrieve(url, filename)
            except urllib.ContentTooShortError as e:
                log.warn("%s\tContentTooShortError\t%i" % (url, i))
            else:
                log.info("%s\t%s" % (sbid, url))
                return True
        log.error("%s\t%s" % (sbid, url))
        return False

    if url.endswith('.pdf'):
        _urlretrieve(url, os.path.join(output_folder, "%s.pdf" % sbid), sbid)
    else:
        page = urllib2.urlopen(url).read()
        soup = bs4.BeautifulSoup(page)
        anchors = soup.findAll('a', attrs={'href': re.compile(".pdf$", re.I)})
        if not anchors:
            log.warn("%s\t%s\tNO_PDF_DETECTED" % (sbid, url))
            return None

        for a in anchors:
            href = a['href']
            pdf_name = href.split('/')[-1]
            print 'ORG\t', url
            if href.startswith('http'):
                url = href
            else:
                if not url.endswith('/'):
                    url += '/'
                url += href
            print href, url
            _urlretrieve(url, os.path.join(output_folder, "%s.%s" % (sbid, pdf_name)), sbid)


def get_tasks(csv_filepath):
    l = []
    with open(csv_filepath, 'r') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for row in reader:
            if row['Action'].lower() != 'ignore for now':
                l.append(row)
    return l


def crawl(csv_filepath, output_folder='pdfs'):
    """
    TODO: some task has multiple links (pdfs), how to handle it?
    """
    tasks = get_tasks(csv_filepath)
    completed = set()
    for f in os.listdir(output_folder):
        completed.add(f.split('.')[0])

    for task in tasks:
        try:
            sbid = task['ScienceBaseID']
            url = task['webLinks__uri']
            if sbid in completed:
                continue
            retrieve(url, sbid, output_folder)
        except Exception as e:
            print e
            log.error("%s\t%s\t%s" % (sbid, url, e))

def main(argv):
    print crawl(argv[1], '/scratch/pdfs')


if __name__ == '__main__':
    import sys
    main(sys.argv)
