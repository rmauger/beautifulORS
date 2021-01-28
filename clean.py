import re
from common import logger

# variables for unicode decoding
nbsp = u'\xa0'  # non-breaking space
lf = u'\x0a'    # line feed
hr = u'\x0d'    # hard return
hr2 = '\n'
lq = u'\u2018'  # left single quote
rq = u'\u2017'  # right single quote
lqq = u'\u201c'  # left double quote
rqq = u'\u201d'  # right double quote
sec = u'\xa7'    # unicode section symbol
sex = '§'       # section symbol
sq = "'"        # straight single quote
sqq = '"'       # straight double quote

# regex constants
anyors = r'(\d{1,3}[A-C]?\.\d{3,4})'
mon = r'(January|February|March|April|May|June|July|August|September|October|November|December)'
day = r'([1-2]?\d|30|31)'
year = r'(19|20)\d{2}'
date = fr'{mon} {day}, {year}'


def cleaner(dirty_text, ors):
    h = str(dirty_text).strip()
    h = repl_chars(h)
    h = bracken(h)
    h = h.replace('| |', '|')
    h = h.replace('||', '|')
    h = sec_start(h, ors)
    h = index(h, ors)
    h = clean_up(h)
    return h


def repl_chars(a):
    b = a.replace(sec, sex)
    b = re.sub(fr'({rq}|{lq})', sq, b)
    b = re.sub(fr'({lqq}|{rqq})', sqq, b)
    b = re.sub(r'(_{26,100})([^_])', r'|\g<1>|\g<2>', b)  # picks up long underlines, puts on own line

    b = re.sub(fr'({hr}+)|({lf}{{2,}})|( {{2,}})', r' ', b)
    b = re.sub(fr'({hr}+)|({lf}{{2,}})|( {{2,}})', r' ', b)
    b = re.sub(fr'({hr}+)|({lf}{{2,}})|( {{2,}})', r' ', b)
    b = re.sub(r'\|{2,}', r'|', b)
    b = b.replace(lf, '')
    return b


def bracken(a):
    """Issue, want to set off section notes [2000 c. 123 s.4]  into their own lines.
     However, need to preserve brackets inline for brackets used as blanks for forms (e.g., [ ] No) and
     also for dates & ORS sections referenced in temporary sections, but not formerly or renumbered sec notes.
     E.g. e.g., Section 2 of this 2019 Act [105.163] applies to any judgment entered before, on or
    # after the effective date of this 2019 Act [January 1, 2020]. Done by temporarily turning brackets into braces {}
    Converting remaining brackets to leadlines, then converting braces back to brackets.
    """
    inbrak = r'[^\n\t\r[]|]*?'   # things that would indicate new set of brackets has started & cancels search
    b = re.sub(fr'\[({inbrak}([Ff]ormerly|[Rr]enumbered)[{nbsp} ]{anyors}{inbrak})]', r'|[\g<1>]|', a)  # frmr / rnbrd
    # todo renumbered should have "in" following if in source note
    b = re.sub(fr'\[({inbrak}{anyors})]',  r'{\g<1>}', b)    # bracketed phrase with ORS numbers (except above)
    b = re.sub(fr'\[({date})]', r'{\g<1>}', b)      # bracketed dates
    b = re.sub(fr'\[([{nbsp} ]+)]', r'{\g<1>}', b)   # bracketed forms/blanks
    b = re.sub(fr'[{nbsp} ]*\[([^\n\t\r|[]{{5,400}}?)][{nbsp} ]*', r'|[\g<1>]|', b)    # otherwise sec_note
    b = re.sub(fr'{{({inbrak}{anyors})}}', r'[\g<1>]', b)  # restores ORS numbers *
    b = re.sub(fr'{{({date})}}', r'[\g<1>]', b)      # replace brackets
    b = re.sub(fr'{{([{nbsp} ]+?)}}', r'[\g<1>]', b)   # replace brackets
    return b


def index(a, ors):
    # finding index (ORS w/ trailing tab & phrase not ending in period)
    index_match = fr'[\|{nbsp} ]+({ors}\.\d{{3}}){nbsp}{{2,}} ?([a-zA-Z\0-9"].+?)({nbsp}|\|%)'
    b = re.sub(index_match, r'|%\g<1>|%\g<2>|\g<3>', a)
    b = re.sub(index_match, r'|%\g<1>|%\g<2>|\g<3>', b)
    b = re.sub(index_match, r'|%\g<1>|%\g<2>|\g<3>', b)
    return b


def sec_start(a, ors):
    # leadline match = new line + ORS section + more info until period & space (excluding "U.S. ")
    leadline = fr'\|+[ {nbsp}]{{0,2}}({ors}\.\d{{3}})[ {nbsp}]?([^\|]+?[a-zA-Z0-9\"][^U.S]\.)\"?[\| {nbsp}]+'
    print(leadline)
    # double amends = new line + ORS section ending with '.' and no leadline
    dam = fr'\|+[ {nbsp}]?({ors}\.\d{{3}}\.)[{nbsp} ]*'
    # session law sections (Sec. xx.)
    ses_sec = r'Sec\. \d{1,3}\.'

    b = re.sub(dam, r'|@\g<1>|!', a)
    # TODO any way to make this work for double amended temp sections (e.g., Sec. 22, c 105, 2018 in chp 98)

    b = re.sub(leadline, r'|\g<1>|#\g<2>|!', b)
    b = re.sub(leadline, r'|\g<1>|#\g<2>|!', b)

    '''if session law intro has a leadline, it should have a period before next line break. E.g., Sec. 2. Defintions.'''
    print(fr'({ses_sec})[{nbsp} ]+([^|\n\t\r]{{5,55}}?\.)[{nbsp} |]+')
    b = re.sub(fr'({ses_sec})[{nbsp} ]+([^|\n\t\r]{{5,55}}?\.)[{nbsp} |]+', r'|\g<1>|#\g<2>|!', b)  # with leadlines
    b = re.sub(fr'({ses_sec})[{nbsp} ]+\|*', r'|\g<1>|!', b)    # without leadlines
    # TODO Note sections 'sometimes' have double amends - no obvious solution here, maybe in classifying
    b = re.sub(r'!+', r'!', b)
    return b


def clean_up(a):
    b = re.sub(fr'\|[ ]?{nbsp}{{2,}}\(', r'|(', a)  # todo - can this be moved down? deleting leading spaces for depth
    b = re.sub(r'\| *!+ *\(1\)', r'|(1)', b)  # deleting leading ! for subsection after leadline
    b = re.sub(fr'{nbsp}{{2,}} ?([a-zA-Z0-9_,;\-\'\"(])', r'|\g<1>', b)  # TODO necessary? working? breaking forms?
    b = b.replace('| (', '|(')

    # pulling out leading double parentheses (e.g. (1)(a) or (d)(A) (e)(A)(i), etc.
    db = r'(\|\(.{1,3}\))\('
    while len(re.sub(db, r'\g<1>|(', b)) != len(b):
        b = re.sub(db, r'\g<1>|(', b)

    b = re.sub(fr'[{nbsp }]*\|+', '|', b)
    b = re.sub(fr'[{nbsp }]*\|+', '|', b)

    return b
