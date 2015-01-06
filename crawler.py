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
import urlparse
import threading
import logging
import logging.handlers

import bs4

MINIMUM_PDF_SIZE = 4506
COMPLETED = set()
TASKS = None

def create_logger(filename, logger_name=None):
    logger = logging.getLogger(logger_name or filename)
    fmt = '[%(asctime)s] %(levelname)s %(message)s'
    datefmt = "%Y-%m-%d %H:%M:%S"
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
            log.warn("%s\tDUPLICATED\t%s" % (sbid, url))
            return None

        for i in range(retry):
            try:
                urllib.urlretrieve(url, filename)
            except urllib.ContentTooShortError as e:
                log.warn("%s\tContentTooShortError\t%s\t%i" % (sbid, url, i))
            else:
                log.info("%s\tOK\t%s" % (sbid, url))
                return True
        log.error("%s\tEXCEED_MAXIMUM_RETRY\t%s" % (sbid, url))
        return False

    if url.endswith('.pdf'):
        #: sbid is not unique, so use sbid+pdfname as new name
        pdf_name = url.split('/')[-1].split('.')[0]
        _urlretrieve(url, os.path.join(output_folder, "%s.%s.pdf" % (sbid, pdf_name)), sbid)
    else:
        page = urllib2.urlopen(url).read()
        soup = bs4.BeautifulSoup(page)
        anchors = soup.findAll('a', attrs={'href': re.compile(".pdf$", re.I)})
        if not anchors:
            log.warn("%s\tNO_PDF_DETECTED\t%s" % (sbid, url))
            return None

        for a in anchors:
            href = a['href']
            pdf_name = href.split('/')[-1]
            sub_url = urlparse.urljoin(url, href)
            _urlretrieve(sub_url, os.path.join(output_folder, "%s.%s" % (sbid, pdf_name)), sbid)


def get_tasks(csv_filepath):
    """
    Returns:
        [{'ScienceBaseID': a1b2c3d4, 'webLinks__uri': 'http://balabala'}, {}]
    """
    l = []
    with open(csv_filepath, 'r') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for row in reader:
            if row['Action'].lower() != 'ignore for now':
                l.append(row)
    return l


def crawl(csv_filepath, output_folder='pdfs'):
    """main function
    """
    global TASKS
    TASKS = get_tasks(csv_filepath)
    for f in os.listdir(output_folder):
        filepath = os.path.join(output_folder, f)
        with open(filepath, 'r') as ff:
            head_line = ff.readline()
        #if os.stat(filepath).st_size > MINIMUM_PDF_SIZE:
        if head_line.startswith("%PDF"):
            COMPLETED.add(f.split('.')[0])
        else:
            os.remove(filepath)
            print 'deleted: ', filepath, head_line

    for i in range(128):
        t = threading.Thread(target=crawler, args=(output_folder,))
        t.start()

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()


def crawler(output_folder):
    finished = 0
    print "thread %i has started" % (threading.current_thread().ident)
    global TASKS, COMPLETED
    while True:
        task = None
        try:
            task = TASKS.pop()
        except IndexError:
            print "thread %i finished %i tasks, exiting for no task available"\
                % (threading.current_thread().ident, finished)
            break

        try:
            if not task:
                break
            sbid = task['ScienceBaseID']
            # some webLinks__uri looks like:
            # http://www.springerlink.com/content/p543611u8317w447/?p=a0e7243d602f4bd3b33b2089b2ed92e4&pi=5  ;  http://www.springerlink.com/content/p543611u8317w447/fulltext.pdf
            # since both url will redirect to the same url finally, I did not retrieve them twice
            url = task['webLinks__uri']
            if sbid in COMPLETED:
                continue
            retrieve(url, sbid, output_folder)

            finished += 1
            if finished % 20 == 0:
                print "%i has finished %i" % (threading.current_thread().ident, finished)
        except Exception as e:
            print e, task
            log.error("%s\tUNEXPECTED\t%s\t%s" % (sbid, url, e))


def main(argv):
    print crawl(argv[1], '/scratch/pdfs')


if __name__ == '__main__':
    import sys
    main(sys.argv)
