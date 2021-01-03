# classifies ORS lines into categories:
# - title (unique, should be "Chapter XXX -- TITLE')
# - subtitle
# - index (table of contents info)
# - or_sec (sections or note sections)
# - leadline (leadline explaining ORS section)
# - slug (ORS paragraph with no subsections)
# - subsec (hierachy of indentation, digits (1))
#   - para  (lower alphabet (a) (except 'L'?)
#     - subpara  (upper alphabet (A))
#       - sub2para  (lower roman (i))
#         - sub3para  (upper roman (I))
# - form  (most likely a form or table within the chapter)
# - note_sec  (notes between sections)
# - source_note  (legislative history)
# - dunno (unclassified)

def in_bracs(txt):          # takes in string beginning with "(xxx)" and returns xxx as string.
    t = str(txt)
    if -1 < t.find(r'(') < 3:
        return str(t[t.find(r'(')+1:t.find(r')')])
    else:
        return None


def typer(type_me, ors):         # takes in line, returns best guess of line type
    txt = str(type_me).strip()
    if txt[0:len(ors)] == ors:
        if len(txt) > len(ors)+4:
            return 'index'
        else:
            return 'or_sec'
    if txt[0] == '#':
        return 'leadline'
    if txt[0] == '%':
        return 'index'
    if txt[0] == '[':
        return 'source_note'
    if txt[0:6] == "Note: ":
        return 'note_sec'
    if txt[0:5] == 'Sec. ':
        return 'or_sec'
    in_brac = in_bracs(txt)
    if in_brac is None:
        if txt[0] == '!':
            return 'slug'
        if txt[0:41] == "_________________________________________":
            return 'form_line'
        if txt[0:8] == txt[0:8].upper():
            return 'sub_title'
        if txt[0:8 + len(ors)] == 'Chapter ' + ors:
            return 'title'
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


# variables for def cleaner:

roman = ['iii', 'iv', 'vi', 'vii', 'viii', 'ix', 'xi', 'xii', 'xiii', 'xiv', 'xv']
romanish = ['i', 'ii', 'v', 'x']
prior_para = {
    'i': 'h',
    'ii': 'hh',
    'v': 'u',
    'x': 'w'}       # letter with its preceeding pair


def reclassify(ors_t_list):           # takes in full 2nd clean two column list
    count = -1
    in_form = 0
    title = 0
    for line in ors_t_list:           # iterate through typed list to fix pieces

        count += 1                    # keeping own counter
        if line[0] == 'title':        # make sure title is unique and on line 0
            if title == 0:
                title = 1
                if count > 0:
                    ors_t_list[count], ors_t_list[0] = ors_t_list[0], ors_t_list[count]
            else:
                line[0] = 'dunno'
        if line[0] == 'slug' or line[0] == 'index' or line[0] == 'leadline':    # get rid of intro trigger '! % or #'
            line[1] = line[1][1:]
        if line[0] == 'form_line':
            in_form += 1
        if in_form % 2 == 1:
            try:
                if line[0] == 'sub_title' or line[0] == 'sub2_title' or line[0] == 'dunno':
                    line[0] = 'form_line'
            except Exception as e:
                print('err: ', e, line[0])
        if line[0] == 'eL':                 # for capital L, scroll up until you find an 'h/H'
            for back in range(count):
                if in_bracs(ors_t_list[(count - back)][1]) == 'h':
                    line[0] = 'para'
                    break
                if in_bracs(ors_t_list[(count - back)][1]) == 'H':
                    line[0] = 'sub_para'
                    break
        if line[0] == 'romanish':           # for ambiguous roman characters, look back one paragraph.
            back_one = ors_t_list[(count - 1)]
            if back_one[0] == 'sub2_para' or back_one[0] == 'sub3_para':
                line[0] = 'sub2_para'
            elif back_one[0] == 'sub_para':  # if it's a sub_para, see if last para matched previous letter in alphabet
                for back in range(count):
                    if ors_t_list[back][0] == 'para':
                        if in_bracs(ors_t_list[(count - back)][1]) == prior_para[in_bracs(line[1])]:
                            line[0] = 'para'            # e.g., (i) is just a para after (h)
                            break
                        else:
                            line[0] = 'sub2_para'       # e.g., (i) is start of roman numeral list i, ii, iii...
                            break
            else:
                line[0] = 'para'
        if line[0] == 'ROMANISH':           # for ambiguous roman characters, look back one paragraph.
            back_one = ors_t_list[(count - 1)][0]
            if back_one == 'sub3_para':    # if it's a sub_3 para, then this too is sub3_para.
                line[0] = 'sub3_para'
            elif back_one[0] == 'sub2_para':  # if it's a sub2para, did last sub_para match previous letter in alphabet?
                for back in range(count):
                    if ors_t_list[back][0] == 'sub_para':
                        if in_bracs(ors_t_list[(count - back)][1]) == prior_para[in_bracs(line[1])].upper():
                            line[0] = 'sub_para'
                            break
                        else:
                            line[0] = 'sub3_para'
                            break
            else:
                line[0] = 'sub_para'
