
########
# This script parses Cuneiform's result and extract layout and font information,
# which is extremely useful for Taxonomy
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! Do not change any parameters in this file    !!!
# !!! This script is validated on more than 1000   !!!
# !!! journal articles from 20 publishers 60 years !!!
# !!! to make sure it is robust cross different    !!!
# !!! journals and years.                          !!!
# !!!                                              !!!
# !!! On all journals that we know about, this     !!!
# !!! script detects layout with almost perfect    !!!
# !!! precision and recall                         !!!
# !!!                                              !!!
# !!! It is also surprising that there is no       !!!
# !!! general layout analysis package out there    !!!
# !!! with even remotely-usable quality            !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
########




import os
import re
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import codecs
import math
import string

class MyHTMLParser(HTMLParser):

    current_mask = None
    chars = None
    masks = None

    def init(self):
        self.current_mask = []
        self.chars = []
        self.masks = []

    def handle_starttag(self, tag, attrs):
        self.current_mask.append(tag)
    def handle_endtag(self, tag):
        self.current_mask.pop()
    def handle_data(self, data):
        self.chars.append(data)
        self.masks.append("".join(self.current_mask))
    def handle_entityref(self, name):
        c = unichr(name2codepoint[name])
        self.chars.append(c)
        self.masks.append("".join(self.current_mask))


class Line:
    [pageid, lineid, left, top, right, bottom, content, xboxes] = [None, None, None, None, None, None, None, None]
    
    whatevercandidate = None

    centered = None

    def __init__(self, _pageid, _lineid, _left, _top, _right, _bottom, _content, _xboxes):
        (self.pageid, self.lineid, self.left, self.top, self.right, self.bottom, self.content, self.xboxes) = (_pageid, _lineid, int(_left), int(_top), int(_right), int(_bottom), _content, _xboxes)
        self.whatevercandidate = False
        self.centered = False

    def __repr__(self):
        return self.content

    def height(self):
        return self.bottom - self.top

    def width(self):
        return self.right - self.left


def parse_cunneiform_results_and_extract_layout_font_information(inputfolder):
    fo = codecs.open(inputfolder + "/fonts.text", 'w', 'utf-8')

    PAGEWIDTH = 2163
    parser = MyHTMLParser()
    cuneifiles = []
    for f in os.listdir(inputfolder):
        if f.startswith('cunei'):
            cuneifiles.append(f)

    lines_withdup = []
    for f in sorted(cuneifiles):
        pageid = f.replace('cuneiform-page-', '').replace('.html', '')
        for l in open(inputfolder + "/" + f):
            m = re.search("""<span class='ocr_line' id='(.*?)' title="bbox (.*?) (.*?) (.*?) (.*?)">(.*?)<span class='ocr_cinfo' title="x_bboxes (.*?)">""", l)
            if m:
                (lineid, left, top, right, bottom, content, xboxes) = (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7))
                xboxes = xboxes.split(' ')
                lines_withdup.append(Line(pageid, lineid, left, top, right, bottom, content, xboxes))

    lines_dup1 = []
    # dedup
    crosspage_dup_tally = {}
    for line in lines_withdup:
        overlap = 0
        for l2 in lines_withdup:
            if line == l2: continue
            if line.pageid != l2.pageid: continue
            
            overlap = 1.0*(line.height() + l2.height() - (max(line.bottom, l2.bottom) - min(line.top, l2.top)))/max(line.height(), l2.height())
            if overlap > 0.5:
                break

        if overlap > 0.5:
            #print "REMOVE DUP", line 
            continue

        remove = False
        for l2 in lines_withdup:
            if line == l2: continue
            if line.pageid == l2.pageid: continue

            voverlap = 1.0*(line.height() + l2.height() - (max(line.bottom, l2.bottom) - min(line.top, l2.top)))/max(line.height(), l2.height())
            hoverlap = 1.0*(line.width() + l2.width() - (max(line.right, l2.right) - min(line.left, l2.left)))/max(line.width(), l2.width())

            if hoverlap > 0.5: 
                if line.content == l2.content:
                    if line.content not in crosspage_dup_tally:
                        crosspage_dup_tally[line.content] = 0
                    crosspage_dup_tally[line.content] = crosspage_dup_tally[line.content] + 1
                    line.whatevercandidate = True

        lines_dup1.append(line)

    lines = []
    for l in lines_dup1:
        if l.whatevercandidate == True and crosspage_dup_tally[l.content] > 1:
            continue
        l.whatevercandidate = False
        lines.append(l)

    ####### start extract fonts     
    for line in lines:
        parser.init()
        parser.feed(line.content)

        nchar = 0
        for i in range(0, len(parser.chars)):
            content = parser.chars[i]
            mask = parser.masks[i]
            content = content.decode("utf-8")
            bbox_left = 10000
            bbox_top = 10000
            bbox_right = 0
            bbox_bottom = 0

            local_content = []
            local_box_left = 10000
            local_box_top = 10000
            local_box_right = 0
            local_box_bottom = 0

            for j in range(0, len(content)):

                left = int(line.xboxes[nchar*4])
                top = int(line.xboxes[nchar*4+1])
                right = int(line.xboxes[nchar*4+2])
                bottom = int(line.xboxes[nchar*4+3])

                nchar = nchar + 1

                if left == -1 or top == -1 or right == -1 or bottom == -1:  
                    fo.write('\t'.join(["JUSTWORD", line.pageid, "%d"%local_box_left, "%d"%local_box_top, "%d"%local_box_right, "%d"%local_box_bottom, "".join(local_content)]) + "\n")
                    local_content = []
                    local_box_left = 10000
                    local_box_top = 10000
                    local_box_right = 0
                    local_box_bottom = 0
                    continue

                bbox_left = min(bbox_left, left)
                bbox_top = min(bbox_top, top)
                bbox_right = max(bbox_right, right)
                bbox_bottom = max(bbox_bottom, bottom)

                local_box_left = min(local_box_left, left)
                local_box_top = min(local_box_top, top)
                local_box_right = max(local_box_right, right)
                local_box_bottom = max(local_box_bottom, bottom)
                local_content.append(content[j])

            if 'i' in mask:
                fo.write('\t'.join(["SPECFONT", line.pageid, "%d"%bbox_left, "%d"%bbox_top, "%d"%bbox_right, "%d"%bbox_bottom, content]) + "\n")

            if local_box_left != 10000:
                fo.write('\t'.join(["JUSTWORD", line.pageid, "%d"%local_box_left, "%d"%local_box_top, "%d"%local_box_right, "%d"%local_box_bottom, "".join(local_content)]) + "\n")


    ##### start extract centered lines
    for line in lines:
        left_margin = line.left - 0
        right_margin = PAGEWIDTH - line.right
        delta = math.fabs(left_margin - right_margin)

        if left_margin > 40 and right_margin > 40 and (delta < 40 or (left_margin > 400 and right_margin > 400)):
            line.centered = True
            
    for iline1 in range(0, len(lines)):
        line = lines[iline1]
        if line.centered == True:
            fo.write('\t'.join(["CENTERED", line.pageid, "%d"%line.left, "%d"%line.top, "%d"%line.right, "%d"%line.bottom, line.content.decode("utf-8")]) + "\n")
            
            for iline2 in range(iline1+1, len(lines)):
                line2 = lines[iline2]
                if line2.centered == True:
                    break
                
                index = string.find(line2.content, '<i>')
                if index >= 0 and index < 20:
                    fo.write('\t'.join(["FOLLOWED", line2.pageid, "%d"%line2.left, "%d"%line2.top, "%d"%line2.right, "%d"%line2.bottom, line2.content.decode("utf-8")]) + "\n")


    fo.close()
