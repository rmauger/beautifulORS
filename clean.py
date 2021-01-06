import re

# variables for unicode decoding
nbsp = u'\xa0'  # non-breaking space
lf = u'\x0a'    # line feed
hr = u'\x0d'    # hard return
lq = u'\u2018'  # left single quote
rq = u'\u2017'  # right single quote
lqq = u'\u201c'  # left double quote
rqq = u'\u201d'  # right double quote
sec = u'\xa7'    # unicode section symbol
sex = '§'       # section symbol
sq = "'"        # straight single quote
sqq = '"'       # straight double quote
anyors = r'\d{1,3}[A-C]?\.\d{3,4}'
mon = r'(January|February|March|April|May|June|July|August|September|October|November|December)'
day = r'([1-2]?\d|30|31)'
year = r'(19|20)\d{2}'
date = fr'{mon} {day}, {year}'

def cleaner(dirty_text, ors):
    h = str(dirty_text).strip()
    h = h.replace(sec, sex)
    h = h.replace(rq, sq)
    h = h.replace(lq, sq)
    h = h.replace(lqq, sqq)
    h = h.replace(rqq, sqq)
    h = re.sub(r'(_{21,100})([^_])', r'|\g<1>|\g<2>', h)  # picks up long underlines, puts on own line
    h = h.replace(hr+hr, ' ')
    h = h.replace(hr, ' ')
    h = h.replace('\n', ' ')
    h = h.replace(lf+lf, ' ')
    h = h.replace(lf, '')
    h = h.replace('  ', ' ')
    h = re.sub(fr'(20\d{{2}} EDITION)(.+?){nbsp}', r'|\g<1>|\g<2>|', h)

    # deal with brackets [ ]
    h = re.sub(fr'\[({anyors})]', r'{\g<1>}', h)    # preserve bracketed ORS numbers
    h = re.sub(fr'\[({date})]', r'{\g<1>}', h)      # preserve bracketed dates
    h = re.sub(fr'\[([nbsp ]+?)]', r'{\g<1>}', h)
    # e.g., Section 2 of this 2019 Act [105.163] applies to any judgment entered before, on or /
    # after the effective date of this 2019 Act [January 1, 2020].
    h = h.replace(' [', '|[')       # Otherwise, surround with a hard return
    h = re.sub(r']\|*', r']|', h)
    h = re.sub(fr'{{({anyors})}}', r'[\g<1>]', h)    # replace brackets
    h = re.sub(fr'{{({date})}}', r'[\g<1>]', h)      # replace brackets
    h = re.sub(fr'{{([nbsp ]+?)}}', r'[\g<1>]', h)   # replace brackets

    h = re.sub(fr'[{nbsp} ]+\|', r'|', h)       # delete stray spaces at end of line before hard return
    h = h.replace('| |', '|')
    h = h.replace('||', '|')

    # finding double amends (ORS section ending with '.' and no leadline:
    dam = fr'\|+[ {nbsp}]?({ors}\.\d{{3}}\.)[{nbsp} ]*'
    h = re.sub(dam, r'|@\g<1>|!', h)

    # finding index:
    index_match = fr'[\|{nbsp} ]+({ors}\.\d{{3}}){nbsp}{nbsp}+ ?([a-zA-Z\0-9"].+?)({nbsp}|\|%)'  # index: trailing tab & no period
    h = re.sub(index_match, r'|%\g<1>|%\g<2>|\g<3>', h)
    h = re.sub(index_match, r'|%\g<1>|%\g<2>|\g<3>', h)
    h = re.sub(index_match, r'|%\g<1>|%\g<2>|\g<3>', h)

    # finding leadlines:
    leadline = fr'\|+[ {nbsp}]?[ {nbsp}]?({ors}\.\d{{3}})[ {nbsp}]?([^\|].+?[a-zA-Z0-9\"][^U.S]\.)[\| {nbsp}]+'  # matches new line + ORS section + more info until period & space
    h = re.sub(leadline, r'|\g<1>|#\g<2>|!', h)
    h = re.sub(leadline, r'|\g<1>|#\g<2>|!', h)
    h = re.sub(r'\|!\(1\)', r'|(1)', h)  # deleting leading ! for subsection after leadline

    h = re.sub(fr'\|[ ]?{nbsp}{nbsp}+\(', r'|(', h)  # deleting leading spaces for sub/para
    h = re.sub(fr'(Sec\. \d{{1,3}}\.) ?', r'|\g<1>|!', h)
    h = re.sub(fr'{nbsp}{nbsp}+ ?([a-zA-Z0-9_,;\-\'\"\(])', r'|\g<1>', h)
    h = h.replace('| (', '|(')
    db = r'(\|\(.{1,3}\))\('
    while len(re.sub(db, r'\g<1>|(', h)) != len(h):
        h = re.sub(db, r'\g<1>|(', h)
    return h


def logger(fn, txt):
    with open(fn+'-log.txt', 'w') as log:
        log.write(txt)