# classifies ORS lines into categories:
# - title (unique, should be "Chapter XXX -- TITLE')
# - SUBTITLE
# -   (Sub2title)
# - index (table of contents info)
# - INDEX_SUB (subsection w/in index)
# -    (index2sub) #TODO double check index_sub2
# - or_sec (sections or note sections)
# - leadline (leadline explaining ORS section)
# - slug (ORS paragraph with no subsections)
# - (1) subsec (hierachy of indentation, digits)
#   - (a) para  (lower alphabet (except 'L')
#     - (A) subpara  (upper alphabet)
#       - (i) sub2para  (lower roman)
#         - (I) sub3para  (upper roman)
# - form_start  (most likely a form or table within the chapter)
# -   form
# - form_end    (end of form)
# - note_sec  (notes between sections)
# - source_note  (legislative history)
# - dunno (unclassified)
import re
from common import print_err

# global variables for def cleaner:
roman = ['iii', 'iv', 'vi', 'vii', 'viii', 'ix', 'xi', 'xii', 'xiii', 'xiv', 'xv']
romanish = ['i', 'ii', 'v', 'x']
prior_para = {
    'i': 'h',
    'ii': 'hh',
    'v': 'u',
    'x': 'w'}       # letter with its preceeding pair
nbsp = u'\xa0'

def in_bracs(txt):          # takes in string beginning with "(xxx)" and returns xxx as string.
    t = str(txt)
    if -1 < t.find(r'(') <= 1:     # if right paren is first bracket
        return str(t[t.find(r'(')+1:t.find(r')')])
    else:
        return None


def typer(type_me, ors):         # takes in line, returns best guess of line type
    txt = str(type_me).strip()
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
        return 'slug'
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
                return "subsec"
        except ValueError:
            pass
        if in_brac == in_brac.upper():
            if in_brac == 'L':
                return 'eL'
            else:
                for i in roman:
                    if in_brac == i.upper():
                        return 'sub3para'
                for i in romanish:
                    if in_brac == i.upper():
                        return 'ROMANISH'
                is_para = True
                for i in in_brac:
                    if i != in_brac[0]:         # making sure all the characters are the same before calling it subpara
                        is_para = False
                if is_para:
                    return 'subpara'
                else:
                    return 'sub2title'
        else:  # if lower case & bracketed
            for i in roman:
                if in_brac == i:
                    return 'sub2para'
            for i in romanish:
                if in_brac == i:
                    return 'romanish'
            is_para = True
            for i in in_brac:
                if i != in_brac[0]:  # making sure all the characters are the same before calling it para
                    is_para = False
            if is_para:
                return 'para'
            else:
                return 'sub2title'
    if txt[0:41] == "_________________________________________":
        return 'form_start'
    if txt[0:8] == txt[0:8].upper():
        return 'subtitle'
    if txt[0:8 + len(ors)] == 'Chapter ' + ors:
        return 'title'
    return 'dunno'


def reclassify(typed_list, ors):           # takes in full 2nd clean two column list
    count = -1
    in_form = False
    title = 0
    for line in typed_list:           # iterate through typed list to fix pieces
        count += 1                    # keeping own counter
        if line[0] == 'title':        # make sure title is unique and on line 0
            if title == 0:
                title = 1
                if count > 0:
                    typed_list[count], typed_list[0] = typed_list[0], typed_list[count]
            else:
                print_err(f'Repeated title found during reclassification', f'For {line}')
                line[0] = 'dunno'
        if (line[0] != 'slug' and line[0] != 'index' and line[0] != 'leadline'
                and line[0] != 'subtitle' and line[0] != 'da_sec') or re.match(r'[a-zA-Z0-9(]', line[1][0]):
            pass
        else:  # get rid of line intro trigger '!, %, ^, @ or #'
            line[1] = line[1][1:]

        # finding beginning, middle & end of a form
        if line[0] == 'form_start':
            line[1] = '##'
            if typed_list[count+1][0] == 'form_ start':          # if series of blank lines, not part of form
                num = 1
                while typed_list[count + num][0] == 'form_start':
                    typed_list[count + num][0] = 'slug'
                    num += 1
                typed_list[count + num][0] = 'slug'     # pick up the last one outside the while loop
            else:
                if in_form:
                    line[0] = 'form'                    # don't try to start a new form if we're already in one
                else:
                    line.append(typed_list[count - 1][0])     # puts parent into form data (3rd slot)
            in_form = True
        if in_form:
            if line[0] == 'subtitle' or line[0] == 'sub2title' or line[0] == 'dunno' or line[0] == 'slug':
                line[0] = 'form'
            else:
                if line[0] == 'form_start' or line[0] == 'form':
                    pass
                else:
                    in_form = False

        if line[0] != 'form' and line[0] != 'index':       # splitting on nbsp when not in form
            line[1] = re.sub(fr'^[ {nbsp}]', '', line[1])    # delete first space in line
            while len(line[1]) != len(re.sub(f'{nbsp}{nbsp}', nbsp, line[1])):
                line[1] = re.sub(f'{nbsp}{nbsp}', nbsp, line[1])
            line[1] = re.sub(fr'U.S.C.{nbsp}+', r'U.S.C. ', line[1])
            if re.search(nbsp, line[1]):
                num = 0
                for i in line[1].split(nbsp):
                    if num > 0:
                        typed_list.insert(count+num, [typer(i, ors), i])
                    num += 1
                line[1] = line[1].split(nbsp)[0]

        if line[0] == 'subtitle':   # replace subtitles coming after index terms as within index.
            try:
                temp = 0
                while typed_list[count + temp][0] == 'sub2title' or typed_list[count + temp][0] == 'subtitle' or \
                        typed_list[count + temp][0] == 'dunno' or typed_list[count + temp][0] == 'index':
                    if typed_list[count + temp][0] == 'index':
                        line[0] = 'index_sub'
                        break
                    temp += 1
            except Exception as e:
                print_err(e, f'line #{count} for: {line}')
        if line[0] == 'sub2title' or line[0] == 'dunno':   # replace subtitles coming after index terms as within index.
            try:
                temp = 0
                while typed_list[count + temp][0] == 'sub2title' or typed_list[count + temp][0] == 'subtitle' or \
                        typed_list[count + temp][0] == 'dunno' or typed_list[count + temp][0] == 'index':
                    if typed_list[count + temp][0] == 'index':
                        line[0] = 'index2sub'
                    temp += 1
            except Exception as e:
                print_err(e, f'sub2title -> index reclass in line# {count} for: {line}')

        # classifying note secs
        if line[0] == 'note_sec':           # classifying note secs
            if re.search(fr'The amendments to ({ors}|section)', line[1]):
                line[0] = 'note_both'
            elif re.search(r'Sections? \d{1,2}.+chapter', line[1]):
                line[0] = 'note_next'
            else:
                line[0] = 'note_prev'
        # TODO depreciate or re-evaluate whether identifying note type can be used successfully

        # Dealing with unique issues involving classifying subdivisions
        if line[0] == 'eL':                 # for capital L, scroll up until you find an 'h/H'
            for back in range(count):
                if in_bracs(typed_list[(count - back)][1]) == 'h':
                    line[0] = 'para'
                    break
                if in_bracs(typed_list[(count - back)][1]) == 'H':
                    line[0] = 'subpara'
                    break

        if line[0] == 'romanish':           # for ambiguous roman characters
            back_one = typed_list[(count - 1)]      # first look back one paragraph, that may answer it
            if back_one[0] == 'sub2para' or back_one[0] == 'sub3para':  # if (i) or (I)...
                line[0] = 'sub2para'
            elif back_one[0] == 'subpara':  # if a subpara (A), did last para (a) match previous letter in alphabet?
                for back in range(count):
                    if typed_list[back][0] == 'para':
                        if in_bracs(typed_list[(count - back)][1]) == prior_para[in_bracs(line[1])]:
                            line[0] = 'para'            # e.g., (i) is just a para after (h)
                            break
                        else:
                            line[0] = 'sub2para'       # e.g., (i) is start of roman numeral list i, ii, iii...
                            break
            else:
                line[0] = 'para'

        if line[0] == 'ROMANISH':           # for ambiguous ROMAN characters, look back one paragraph.
            back_one = typed_list[(count - 1)][0]
            if back_one == 'sub3para':    # if it's a sub3 para (I), then this too is sub3para (II).
                line[0] = 'sub3para'
            elif back_one == 'sub2para':  # if a sub2para (i), did last subpara (A) match previous letter?
                for back in range(count,1, -1):
                    if typed_list[back][0] == 'subpara':
                        if in_bracs(typed_list[back][1]) == prior_para[in_bracs(line[1]).lower()]:
                            line[0] = 'subpara'
                            break
                        else:
                            line[0] = 'sub3para'
                            break
            else:
                line[0] = 'subpara'

        if line[0] == 'dunno':
            print_err(f'unclassified line ("dunno") remains', f'Line #{count} for {line}')
