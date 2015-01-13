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
import time
import random

import bs4

MINIMUM_PDF_SIZE = 4506
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


class ExceedMaximumRetryError(Exception):
    def __init__(self, sbid, url):
        self.sbid = sbid
        self.url = url


def retrieve(url, sbid, output_folder):
    """Download the PDF or search for the webpage for any PDF link
    Args:
        url, assuming the input url is valid
    """
    def _urlfetch(url, sbid, filename=None, retry=10):
        """
        A wrapper for either urlopen or urlretrieve. It depends on the whether
        there is a filename as input
        """
        if filename and os.path.exists(filename):
            log.warn("%s\tDUPLICATED\t%s" % (sbid, url))
            return None

        sleep_time = random.random() + 0.5
        for i in range(1, retry+1):
            try:
                result = None
                if filename:
                    result = urllib.urlretrieve(url, filename)
                    log.info("%s\tOK\t%s" % (sbid, url))
                else:
                    # No log now, because later we would like to ensure
                    # the existance of PDFs
                    result = urllib2.urlopen(url).read()
                return result
            except urllib.ContentTooShortError as e:
                log.warn("%s\tContentTooShortError\t%s\tRetry:%i&Sleep:%.2f" %
                        (sbid, url, i, sleep_time))
                time.sleep(sleep_time)
            except urllib2.HTTPError as e:
                log.warn("%s\tHTTP%i\t%s\tRetry:%i&Sleep:%.2f\t%s" %
                        (sbid, e.code, url, i, sleep_time, e.reason))
                time.sleep(sleep_time)
                # Sleep longer if it is server error
                # http://en.wikipedia.org/wiki/Exponential_backoff
                if e.code / 100 == 5:
                    sleep_time = random.randint(0, 2 ** i - 1)
            except urllib2.URLError as e:
                log.warn("%s\tURLError\t%s\tRetry:%i&Sleep:%.2f\t%s" %
                    (sbid, url, i, sleep_time, e.reason))
                time.sleep(sleep_time)
        raise ExceedMaximumRetryError(sbid=sbid, url=url)

    if url.endswith('.pdf'):
        #: sbid is not unique, so use sbid+pdfname as new name
        pdf_name = url.split('/')[-1].split('.')[0]
        _urlfetch(url, sbid, os.path.join(output_folder, "%s.%s.pdf" % (sbid, pdf_name)))
    else:
        page = _urlfetch(url, sbid)
        soup = bs4.BeautifulSoup(page)
        anchors = soup.findAll('a', attrs={'href': re.compile(".pdf$", re.I)})
        if not anchors:
            log.warn("%s\tNO_PDF_DETECTED\t%s" % (sbid, url))
            return None

        for a in anchors:
            href = a['href']
            pdf_name = href.split('/')[-1]
            sub_url = urlparse.urljoin(url, href)
            _urlfetch(sub_url, sbid, os.path.join(output_folder, "%s.%s" % (sbid, pdf_name)))


def get_tasks(csv_filepath):
    """
    Returns:
        [{'ScienceBaseID': a1b2c3d4, 'webLinks__uri': 'http://balabala'}, {}]
    """
    l = []
    with open(csv_filepath, 'r') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for row in reader:
            if 'Action' in row and row['Action'].lower() == 'ignore for now':
                continue
            else:
                l.append(row)
    return l


def get_completed_tasks(output_folder):
    """
    Return downloaded tasks
    """
    completed = set()
    for f in os.listdir(output_folder):
        filepath = os.path.join(output_folder, f)
        with open(filepath, 'r') as ff:
            head_line = ff.readline()
        #if os.stat(filepath).st_size > MINIMUM_PDF_SIZE:
        if head_line.startswith("%PDF"):
            completed.add(f.split('.')[0])
        else:
            os.remove(filepath)
            print 'deleted: ', filepath, head_line
    return completed


def crawl(csv_filepath, output_folder='pdfs', exclude_downloaded=False):
    """main function
    """
    global TASKS
    TASKS = get_tasks(csv_filepath)

    excluded = set()
    if exclude_downloaded:
        excluded = get_completed_tasks(output_folder)

    for i in range(128):
        t = threading.Thread(target=crawler, args=(output_folder, excluded))
        t.start()

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()


def crawler(output_folder, excluded=set()):
    """
    Thread working function
    """
    finished = 0
    print "thread %i has started, exclude %i items" %\
        (threading.current_thread().ident, len(excluded))
    global TASKS

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
            if sbid in excluded:
                continue
            retrieve(url, sbid, output_folder)

            finished += 1
            if finished % 20 == 0:
                print "%i has finished %i" % (threading.current_thread().ident, finished)
        except ExceedMaximumRetryError as e:
            log.error("%s\tEXCEED_MAXIMUM_RETRY\t%s" % (e.sbid, e.url))
        except Exception as e:
            print e, task
            log.error("%s\tUNEXPECTED\t%s\t%s" % (sbid, url, e))


def main(argv):
    print crawl(argv[1], '/scratch/pdfs')


if __name__ == '__main__':
    import sys
    main(sys.argv)
