'''classifies ORS lines into categories:
- title (unique, should be "Chapter XXX -- TITLE')
- SUBTITLE
-   (Sub2title)
- index (table of contents info)
- INDEX_SUB (subsection w/in index)
-    (index2sub)
- or_sec (sections or note sections)
- leadline (leadline explaining ORS section)
- 0 slug (ORS paragraph with no subsections)
- 1 (1) subsec (hierachy of indentation, digits)
  - 2 (a) para  (lower alphabet (except 'L')
    - 3 (A) subpara  (upper alphabet)
      - 4 (i) sub2para  (lower roman)
        - 5 (I) sub3para  (upper roman)
- form_start  (most likely a form or table within the chapter)
-   form
- form_end    (end of form)
- note_sec  (notes between sections)
- source_note  (legislative history)
- dunno (unclassified)'''


import re
from common import print_err

# global fixed variables for def cleaner:
roman = ['iii', 'iv', 'vi', 'vii', 'viii', 'ix', 'xi', 'xii', 'xiii', 'xiv', 'xv']
romanish = ['i', 'ii', 'v', 'x']
prior_para = {
    'i': 'h',
    'ii': 'hh',
    'v': 'u',
    'x': 'w'}       # letter with its preceeding pair
nbsp = u'\xa0'

# global variables assigned/used during program
in_form = None
count = 0
ors = 0
form_starter = None
form_ender = []


def in_bracs(txt):          # takes in string beginning with "?(xxx)" and returns xxx as string.
    t = str(txt)
    if -1 < t.find(r'(') <= 1:     # if right paren is first bracket
        return str(t[t.find(r'(')+1:t.find(r')')])
        # todo could probably make regex entire program here, but if it ain't broke
    else:
        return None


def typer(type_me, chp):         # takes in line, returns best guess of line type
    global ors
    ors = chp
    txt = str(type_me).strip()
    if txt[1:(9 + len(ors))] == f'Chapter {ors}' or txt[0:(8 + len(ors))] == f'Chapter {ors}':
        return 'title'
    if txt[0] == '#':
        return 'leadline'
    elif txt[0] == '%':
        return 'index'
    elif txt[0] == '[':
        return 'source_note'
    elif txt[0] == '^':
        return 'subtitle'
    elif txt[0] == '@':
        return 'da_sec'
    elif txt[0] == '!':
        return 0
    elif re.search(r'Note( \d{1,2})?: ', txt[0:9]):
        return 'note_sec'
    elif txt[0:5] == 'Sec. ':
        return 'temp_sec'
    elif txt[0:len(ors)] == ors:
        if len(txt) == len(ors)+4:
            return 'or_sec'
    in_brac = in_bracs(txt)
    if in_brac is not None:
        try:
            if int(in_brac) != 0:
                return 1
        except ValueError:
            pass
        if in_brac == in_brac.upper():
            if in_brac == 'L' or in_brac == 'LL' or in_brac=='LLL':
                return 'eL'
            else:
                for i in roman:
                    if in_brac == i.upper():
                        return 5                # sub3para
                for i in romanish:
                    if in_brac == i.upper():
                        return 'ROMANISH'
                is_para = True
                for i in in_brac:
                    if i != in_brac[0]:         # making sure all the characters are the same before calling it subpara
                        is_para = False
                if is_para:
                    return 3        # subpara
                else:
                    return 'sub2title'
        else:  # if lower case & bracketed
            for i in roman:
                if in_brac == i:
                    return 4        # sub2para
            for i in romanish:
                if in_brac == i:
                    return 'romanish'
            is_para = True
            for i in in_brac:
                if i != in_brac[0]:  # making sure all the characters are the same before calling it para
                    is_para = False
            if is_para:
                return 2            # para
            else:
                return 'sub2title'
    if txt[0:41] == "_________________________________________":
        return 'form_start'
    if txt[0:8] == txt[0:8].upper():
        return 'subtitle'
    return 'dunno'


def reclassify(typed_list):      # takes in full 2nd clean two column list
    global ors
    global in_form
    global count
    count = -1
    in_form = False
    for line in typed_list:           # iterate through typed list to fix pieces
        count += 1                    # keeping own counter to match index (0 to end)
        if (line[0] == 0 or line[0] == 'index' or line[0] == 'leadline' or line[0] == 'form' or
                line[0] == 'subtitle' or line[0] == 'da_sec' or line[0] == 'title') and not \
                re.search(r'[a-zA-Z0-9(\"]', line[1][0]):
            line[1] = line[1][1:]               # get rid of line intro trigger '!, %, ^, @ or #'

        check_form(line, typed_list)
        check_index(line, typed_list)
        check_note(line)
        line[0] = fix_subs(line[0], typed_list)
        if str(line[0]).isnumeric():                    # adds full cite to item
            line.append(get_cite(typed_list, count))


def check_form(fl, lst):   # checks *formline* to determine if in form, based in part on surrounding members of *list*
    global in_form
    global count
    global ors
    global form_starter
    global form_ender
    if fl[0] == 'form_start':
        fl[1] = '##'
        if lst[count+1][0] == 'form_ start':          # if series of blank lines, not part of form
            num = 1
            while lst[count + num][0] == 'form_start':
                lst[count + num][0] = 0
                num += 1
            lst[count + num][0] = 0     # pick up the last one outside the while loop
        else:
            if in_form:
                fl[0] = 'form'                    # don't try to start a new form if we're already in one
            else:
                form_starter = lst[count - 1]
                fl.append(form_starter[0])     # puts parent type into form data (3rd slot)
                parenmatch = r'\(.\)'
                mycite = get_cite(lst, count-1)
                a = 0
                for match in re.finditer(parenmatch, mycite):
                    st = match.start()+1
                    end = match.end()-1
                    char = mycite[st:end]
                    a += 1
                    if a == 1:
                        form_ender.append((str(int(char)+1)))
                    elif (a == 2 or a == 3) and len(char) == 1:
                        form_ender.append(chr(ord(char)+1))
                    elif a == 4 or a == 5:
                        pass  # todo is there any possible way to add roman numerals (could just make a library/list?)
        in_form = True
    if in_form:
        if fl[0] == 'subtitle' or fl[0] == 'sub2title' or fl[0] == 'dunno' or fl[0] == 0:
            fl[0] = 'form'
        else:  # check to see if next depth or a new section / source note that will end our form
            if str(fl[0]).isnumeric:
                if in_bracs(fl[1]) in form_ender:
                    in_form = False
                    form_starter = None
                    form_ender = []
            if fl[0] == 'or_sec' or fl[0] == 'source_note':
                in_form = False
                form_starter = None
                form_ender = []

    # Separate below into split function
    if fl[0] != 'form' and fl[0] != 'index':       # splitting on nbsp when not in form
        fl[1] = re.sub(fr'^[ {nbsp}]', '', fl[1])    # delete first space in line
        while len(fl[1]) != len(re.sub(f'{nbsp}{nbsp}', nbsp, fl[1])):
            fl[1] = re.sub(f'{nbsp}{nbsp}', nbsp, fl[1])
        fl[1] = re.sub(fr'U.S.C.{nbsp}+', r'U.S.C. ', fl[1])  # TODO Move to cleaning
        if re.search(nbsp, fl[1]):
            num = 0
            for i in fl[1].split(nbsp):
                if num > 0:
                    lst.insert(count+num, [typer(i, ors), i])
                    # todo if typer returns a "dunno" change nbsp to space & remerge lines?
                num += 1
            fl[1] = fl[1].split(nbsp)[0]


def get_cite(alist, cnt):

    def back_track(findme):
        num = 0
        while True:
            if alist[cnt-1-num][0] == findme:
                if (in_bracs(alist[cnt-1-num][1])) is None:
                    return alist[cnt-1-num][1]
                else:
                    return in_bracs(alist[cnt-1-num][1])
            num += 1
            if cnt-1-num < 0:
                return "NOT FOUND"

    my_cite = ''
    for i in range(4, 0, -1):              # cycle backwards through depth (5 -> 1)
        if alist[cnt][0] > i:             # (subsec)(para)(subpara)(sub2para)(sub3para)
            my_cite = f'({back_track(i)}){my_cite}'
        if alist[cnt][0] == i:
            my_cite = f'({in_bracs(alist[cnt][1])}){my_cite}'
    section = back_track('or_sec')
    if re.search(r'\d{1,3}[A-C]?\.\d{3,4}', section):
        my_cite = f'ORS {section} {my_cite}'
    else:
        my_cite = f'Sec. {section}. {my_cite}'
    return my_cite


def check_index(il, lst):
    global count
    if il[0] == 'subtitle':   # replace subtitles coming after index terms as within index.
        try:
            temp = 0
            while lst[count + temp][0] == 'sub2title' or lst[count + temp][0] == 'subtitle' or \
                    lst[count + temp][0] == 'dunno' or lst[count + temp][0] == 'index':
                if lst[count + temp][0] == 'index':
                    il[0] = 'index_sub'
                    break
                temp += 1
        except Exception as e:
            print_err(e, f'line #{count} for: {il}')
    if il[0] == 'sub2title' or il[0] == 'dunno':   # replace subtitles coming after index terms as within index.
        try:
            temp = 0
            while lst[count + temp][0] == 'sub2title' or lst[count + temp][0] == 'subtitle' or \
                    lst[count + temp][0] == 'dunno' or lst[count + temp][0] == 'index':
                if lst[count + temp][0] == 'index':
                    il[0] = 'index2sub'
                temp += 1
        except Exception as e:
            print_err(e, f'sub2title -> index reclass in line# {count} for: {il}')


def check_note(nl):
    # classifying note secs
    global ors
    if nl[0] == 'note_sec':  # classifying note secs
        if re.search(r'Sections? \d{1,3}.+chapter', nl[1]):
            nl[0] = 'note_next'
        else:
            nl[0] = 'note_prev'


def del_intro(typed_list):
    del_on = False
    for i in range(len(typed_list)-1, -1, -1):
        if del_on:
            typed_list.remove(typed_list[i])
        if typed_list[i][0] == 'title':
            del_on = True


def fix_subs(cur, lst):
    if cur == 'eL':  # for capital L, scroll up until you find an 'h/H'
        for back in range(count):
            if in_bracs(lst[(count - back)][1]) == 'h':
                return 2
            if in_bracs(lst[(count - back)][1]) == 'H':
                return 3
    elif cur == 'romanish':  # for ambiguous roman characters
        # TODO see todos below combine these a little better? Make separate function.
        back_one = lst[(count - 1)]  # first look back one paragraph, that may answer it
        if back_one[0] == 4 or back_one[0] == 5:  # if (i) or (I)...
            return 4
        elif back_one[0] == 3:  # if a subpara (A), did last para (a) match previous letter in alphabet?
            for back in range(count):
                if lst[back][0] == 2:
                    if in_bracs(lst[(count - back)][1]) == prior_para[in_bracs(lst[count][1])]:
                        return 2  # e.g., (i) is just a para after (h)
                    else:
                        return 4  # e.g., (i) is start of roman numeral list i, ii, iii...
        else:
            return 2
    elif cur == 'ROMANISH':  # for ambiguous ROMAN characters, look back one paragraph.
        back_one = lst[(count - 1)][0]
        if back_one == 5:  # if it's a sub3 para (I), then this too is sub3para (II).
            # TODO not necesarily. Should still check. Could be (g), **(h),** (A), (B), (i), (ii), **(i),** (j)...
            return 5
        elif back_one == 4:  # if a sub2para (i), did last subpara (A) match previous letter?
            for back in range(count, 1, -1):
                # TODO could probalby use backward count above and for entire piece where we need to look back.
                # todo see back_track function elsewhere & maybe incorporate it
                if lst[back][0] == 3:
                    if in_bracs(lst[back][1]) == prior_para[in_bracs(lst[count][1]).lower()]:
                        return 3
                    else:
                        return 5
        else:
            return 3
    elif cur == 'dunno':
        print_err(f'unclassified line ("dunno") remains', f'Line #{count} for {cur}')
        return cur
    else:
        return cur
