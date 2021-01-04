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


def cleaner(dirty_text, ors):
    ors_match = fr'{ors}\.\d{{3}}'
    h = str(dirty_text).strip()
    h = h.replace(sec, sex)
    h = h.replace(rq, sq)
    h = h.replace(lq, sq)
    h = h.replace(lqq, sqq)
    h = h.replace(rqq, sqq)
    h = re.sub(r'_{21,100}', r'|\g<0>|', h)  # picks up long underlines, puts on own line
    h = h.replace(hr+hr, ' ')
    h = h.replace(hr, ' ')
    h = h.replace('\n', ' ')
    h = h.replace(lf+lf, ' ')
    h = h.replace(lf, '')
    h = re.sub(fr'(20\d{{2}} EDITION)(.+?){nbsp}', r'|\g<1>|\g<2>|', h)
    h = h.replace('  ', ' ')
    h = h.replace(' [', '|[')
    h = re.sub(r'\]\|*', r']|', h)
    h = re.sub(fr'[{nbsp} ]\|', r'|', h)
    h = h.replace('| |', '|')
    h = h.replace('||', '|')
    # finding index:
    index_match = fr'[\|{nbsp} ]+({ors}\.\d{{3}}){nbsp}{nbsp}+ ?([a-zA-Z].+?)({nbsp}|\|%)'  # index: trailing tab & no period
    print(f'index: {index_match}')
    logger('index', h)
    h = re.sub(index_match, fr'|%\g<1>|%\g<2>|\g<3>', h)
#    logger('index2', h)
    h = re.sub(index_match, fr'|%\g<1>|%\g<2>|\g<3>', h)
    h = re.sub(index_match, r'|%\g<1>|%\g<2>|\g<3>', h)
    # finding leadlines:
    leadline = fr'\|+[ {nbsp}]?[ {nbsp}]?({ors}\.\d{{3}})[ {nbsp}]?([^\|].+?[a-zA-Z]\.)[\| {nbsp}]+'  # matches new line + ORS section + more info until period & space
    print(f'leadline: {leadline}')
#    logger('leadline', h)
    # for i in h.split('|'):
    #     if re.match(r'93\.180', i):
    #         print(i.encode('utf-8'))
    h = re.sub(leadline, r'|\g<1>|#\g<2>|!', h)
#    logger('leadline2', h)
    h = re.sub(leadline, r'|\g<1>|#\g<2>|!', h)
    h = re.sub(r'\|!\(1\)', r'|(1)', h)  # deleting leading ! for subsection after leadline
    h = re.sub(fr'\|[ ]?{nbsp}{nbsp}+\(', r'|(', h)  # deleting leading spaces for sub/para
    h = re.sub(r'(^Sec. \d+\.) ', r'\g<1>|!', h)
    h = re.sub(fr'{nbsp}{nbsp}+ ?([a-zA-Z0-9_,;\-\'\"\(])', r'|\g<1>', h)
    h = h.replace('| (', '|(')
    db = r'(\|\(.{1,3}\))\('
    print(db)
    while len(re.sub(db, r'\g<1>|(', h)) != len(h):
        print('found one')
        h = re.sub(db, r'\g<1>|(', h)
    return h

def logger(fn, txt):
    with open(fn+'-log.txt', 'w') as log:
        log.write(txt)