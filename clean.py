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
    h = h.replace(hr+hr, '|')
    h = h.replace(hr, ' ')
    h = h.replace(lf+lf, '|')
    h = h.replace(lf, '')
    h = h.replace('^!', '|')
    h = h.replace('%!', '|')
    index_match = fr'[{nbsp} ]+({ors}\.\d{{3}}){nbsp}{nbsp}+ ?'  # index: trailing tab & no period
    print(index_match)
    h = re.sub(index_match, r'|%\g<1>|%', h)
    leadline = fr'\|({ors}\.\d{{3}}) (.+?\.) '      # matches new line + ORS section + more info until period & space
    print(leadline)
    h = re.sub(leadline, r'|\g<1>|#\g<2>|!', h)
    h = re.sub(r'\|!\(1\) ', r'|(1) ', h)  #
    h = re.sub(r'(^Sec. \d+\.) ', r'\g<1>|!', h)
#    h = re.sub(r'\|' + nbsp + nbsp + fr'+ ?([a-zA-Z0-9_\-,;\'\"])', r'|\g<1>', h) # TODO Was this anything?
    while h.find(r')(', h.find(')|('), 10) > 1:                 # replace first )( in, e.g. (1)(a) or (2)(b)(C)
        h = re.sub(r'\)\(', r')|(', h, count=1)  # TODO (LOW) needs checked & verified
    h = h.replace(' [', '|[')
    h = h.replace('||', '|')
    return h
