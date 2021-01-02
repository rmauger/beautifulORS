import re

# variables for unicode decoding
nbsp = u'\xa0'  # non-breaking space
lf = u'\x0a'    # line feed
hr = u'\x0d'    # hard return
lq = u'\u2018'  # left single quote
rq = u'\x92'  # right single quote
lqq = u'\u201c'  # left double quote
rqq = u'\u201d'  # right double quote
sec = u'\xa7'    # unicode section symbol
sex = '§'       # section symbol
sq = "'"        # straight single quote
sqq = '"'       # straight double quote

counter = 0

# variables for def cleaner:

roman = ['iii', 'iv', 'vi', 'vii', 'viii', 'ix', 'xi', 'xii', 'xiii', 'xiv', 'xv']
romanish = ['i', 'ii', 'v', 'x']


def in_bracs(txt):          # takes in string beginning with "(xxx)" and returns xxx as string.
    t = str(txt)
    if -1 < t.find(r'(') < 3:
        return str(t[t.find(r'(')+1:t.find(r')')])
    else:
        return None


def cleaner(dirty_text, ors):
    lead_match = rf'(\|{ors}\.\d{{3}})\| ([a-zA-Z0-9_\-,;\'\" ]+\.) '
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
    h = re.sub(nbsp + nbsp + fr'+ ?({ors}\.\d{{3}})', r'|!!\g<1>!!|', h)
    h = re.sub(nbsp+rf' ?({ors}\.\d{{3}})', r'|??\g<1>??|', h)  # replaces 2+ spaces before ORS with new line
    h = re.sub(lead_match, r'|\g<1>|#\g<2>|!', h)  # replaces leadline with new line
    h = re.sub(r'\|!\(1\) ', r'|(1) ', h)
    h = re.sub(r'(^Sec. \d+.) ', r'\g<1>|!', h)
    h = h.replace(r'\|\|', r'|')
    h = re.sub(r'\|' + nbsp + nbsp + fr'+ ?([a-zA-Z0-9])', r'|@@\g<1>@@', h)
    while h.find(r')(', h.find(')|('), 10) > 1:                 # replace first )( in, e.g. (1)(a) or (2)(b)(C)
        h = re.sub(r'\)\(', r')|(', h, count=1)  # TODO move to line by line cleaning
    h = h.replace(' [', '|[')
    h = h.strip()
    h = h.replace('|', hr)
    return h


def typer(type_me, chp):                    # returns best guess of line type
    txt = str(type_me).strip()
    if txt[0:len(chp)] == chp:
        if len(txt) > len(chp)+4:
            return "Index"
        else:
            return 'Or_sec'
    if txt[0] == '#':
        return 'leadline'
    if txt[0] == '[':
        return 'source_note'
    if txt[0:6] == "Note: ":
        return 'note_sec'
    if txt[0:5] == "Sec. ":
        return 'or_sec'
    in_brac = in_bracs(txt)
    if in_brac is None:
        if txt[0:41] == "_________________________________________":
            return 'form_line'
        if txt[0:8] == txt[0:8].upper():
            return 'sub_title'
        if txt[0:8 + len(chp)] == 'Chapter ' + chp:
            return 'title'
        if txt[0] == '!':
            return 'slug'
        else:
            return 'dunno'
    else:
        if len(in_brac) > 5:
            return 'sub2_title'
        try:
            if int(in_brac) != 0:
                return "sub_sec"
        except ValueError:
            pass
        if in_brac == in_brac.upper():
            if in_brac != 'L':
                for i in roman:
                    if in_brac == i.upper():
                        return 'sub3_para'
                for i in romanish:
                    if in_brac == i.upper():
                        return 'ROMANISH'
                return 'sub_para'
            else:
                return 'eL'
        else:  # if lower case & bracketed
            for i in roman:
                if in_brac == i:
                    return 'sub2_para'
            for i in romanish:
                if in_brac == i:
                    return 'romanish'
            return 'para'


def third_clean(ors_line):           # takes in full 2nd clean two column list, returns 3 column list
    prior_para = {
        'i': 'h',
        'ii': 'hh',
        'v': 'u',
        'x': 'w'}
    count = -1
    in_form = 0
    for line in ors_line:           # iterate through list to fix pieces
        count += 1
        if line[0] == 'form_line':
            in_form += 1
        if in_form % 2 == 1:
            try:
                if line[0] == 'sub_title' or line[0] == 'sub2_title' or line[0] == 'dunno':
                    line[0] = 'form_line'
            except Exception as e:
                print('err: ', e, line[0])
        if line[0] == 'eL':                 # for capital L, scroll up until you find an 'h'
            for back in range(count):
                if in_bracs(ors_line[(count - back)][1]) == 'h':
                    line[0] = 'para'
                    break
                if in_bracs(ors_line[(count - back)][1]) == 'H':
                    line[0] = 'sub_para'
                    break
        if line[0] == 'romanish':           # for ambiguous roman characters, look back one paragraph.
            back_one = ors_line[(count - 1)]
            if back_one[0] == 'sub2_para' or back_one[0] == 'sub3_para':
                line[0] = 'sub2_para'
            elif back_one[0] == 'sub_para':  # if it's a sub_para, see if last para matched previous letter in alphabet
                for back in range(count):
                    if ors_line[back][0] == 'para':
                        if in_bracs(ors_line[(count - back)][1]) == prior_para[in_bracs(line[1])]:
                            line[0] = 'para'            # e.g., (i) is just a para after (h)
                            break
                        else:
                            line[0] = 'sub2_para'       # e.g., (i) is start of roman numeral list i, ii, iii...
                            break
            else:
                line[0] = 'para'
        if line[0] == 'ROMANISH':           # for ambiguous roman characters, look back one paragraph.
            back_one = ors_line[(count - 1)][0]
            if back_one == 'sub3_para':    # if it's a sub_3 para, then this too is sub3_para.
                line[0] = 'sub3_para'
            elif back_one[0] == 'sub2_para':  # if it's a sub2para, did last sub_para match previous letter in alphabet?
                for back in range(count):
                    if ors_line[back][0] == 'sub_para':
                        if in_bracs(ors_line[(count - back)][1]) == prior_para[in_bracs(line[1])].upper():
                            line[0] = 'sub_para'
                            break
                        else:
                            line[0] = 'sub3_para'
                            break
            else:
                line[0] = 'sub_para'
