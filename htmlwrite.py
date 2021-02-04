from html3 import HTML
from classify import in_bracs
from bs4 import BeautifulSoup
from common import print_err
import re
from common import error_save


# global variables
sec_div, cur_div, form, err, slug = None, None, None, None, None
subs_list = [HTML(), HTML(), HTML(), HTML(), HTML()]             # depths that can exist
# global constants
start = ('1', 'a', 'A', 'i', 'I')       # things that start a new subdepth

def html_builder(ors_list, chp):
    h = HTML(newlines=True)
    ht = h.html(lang="en-US", newlines=True)
    hd = ht.head(newlines=True)
    hd.link(rel='stylesheet', href='orsstyle.css')
    hd.title(ors_list[0][1])
    body = ht.body(newlines=True)
    body.h1(ors_list[0][1], class_='title')
    build_index(ors_list, chp, body)
    main = body.div(class_='main')
    main.h2('Oregon Revised Statutes', class_='subtitle')
    build_sections(ors_list, main)
    write_html(h)


def build_index(index_list, ors, by):
    ul_ix = None
    ix = by.div(class_='toc', id='chp' + str(ors) + '_index')
    ix.h2('Table of Contents')
    ix_list = None
    for ix_line in index_list:
        if ix_line[0] == 'index_sub':
            ix.h3(ix_line[1])
            ix_list = ix.ul(' ')
        elif ix_line[0] == 'index2sub':
            ix.h4(ix_line[1])
            ix_list = ix.ul(' ')
        elif ix_line[0] == 'index':
            if ix_list is None:
                ix_list = ix.ul(' ')
            if re.match(fr'^{ors}\.\d{{3}}', ix_line[1]):  # ORS number for index
                ul_ix = ix_list.li
                ul_ix.a(ix_line[1], href='#' + (ix_line[1]))
            else:
                ul_ix.span(' ' + ix_line[1])  # Leadline for index


def build_sections(sections_list, mn):
    global sec_div
    global cur_div
    global form
    global err
    global subs_list
    ll, sec_div, cur_div, form, err, = None, None, None, None, None
    counter = 0

    for line in sections_list[1:]:
        counter += 1
        if line[0] == 'index' or line[0] == 'index_sub' or line[0] == 'index2sub':
            pass
        elif line[0] == 'subtitle':
            mn.h3(line[1], class_='subtitle')
        elif line[0] == 'sub2title':
            mn.h4(line[1], class_='sub2title')
        elif line[0] == 'or_sec':
            sec_div = mn.div(id=line[1], class_='section')
            ll = sec_div.p(line[1], class_='or_sec')
            err = None
            cur_div = sec_div
            reboot_cur()
        elif line[0] == 'temp_sec':
            sec_div = mn.div(class_='section temporary')
            ll = sec_div.p(line[1], class_='or_sec')
            cur_div = sec_div
            reboot_cur()
        elif line[0] == 'da_sec':
            alt_div = cur_div.div(class_='alternate')
            cur_div = alt_div
            cur_div.p(line[1], class_='or_sec')
            reboot_cur()
        elif line[0] == 'leadline':
            ll.span(' ' + line[1], class_='leadline')
        elif line[0] == 'note_next':
            mn.p(line[1], class_='note')
        else:
            if sec_children(line, sec_div):
                pass
            elif cur_children(line, cur_div):
                pass
            else:
                print_err('Generated HTML for unclassified line', f'For {line}')
                if err is None:
                    try:
                        err = cur_div.div(class_='unknown')
                    except Exception as e:
                        print_err(e, f'creating new error div failed for {line}')
                        err = mn.div(class_='unknown')
                    err.p("** WARNING ** ", style='font-weight:bold;text-align:center')
                    err.p("Lines below are part of this section, but may not have parsed correctly.",
                          style='font-weight:bold;text-align:center')
                    ptemp = err.p("View original from the ",
                                  style='font-weight:bold;text-align:center;margin-bottom:20px')
                    ptemp.a('Oregon Legislature Website',
                            href='https://www.oregonlegislature.gov/bills_laws/Pages/ORS.aspx')
                    ptemp += '.'
                try:
                    err.p(line[1])
                except Exception as e:
                    print_err(e, f' adding to existing err message failed for {line}')


def reboot_cur():
    global err
    global subs_list
    err = None
    subs_list = [HTML(), HTML(), HTML(), HTML(), HTML()] 


# children of original section:
def sec_children(line, kid_div):        # if it's a note/source note, it goes with original section, not small print
    if line[0] == 'source_note':
        kid_div.p(line[1], class_='source_note')
        return True
    elif line[0] == 'note_prev' or line[0] == 'note_both':
        # TODO note_both can probably be depreciated after confirming with some examples; see classify.py notes
        kid_div.p(line[1], class_='note')
        return True
    else:
        return False


# children of current section:
def cur_children(line, my_div):
    global err
    global slug

    # todo carve out form piece below
    global form
    if line[0] == 'form_start':  # trying to create new form box based on parentage
        try:
            form_id = line[2]  # pulls in parent of form type from prior line todo: although why not just do that now?
            if form_id == 0:
                form = slug.div(class_='form-box')
            # TODO simplify below
            elif str(form_id).isnumeric():
                if 1 <= form_id <= 5:
                    form = subs_list[form_id-1].div(class_='form-box')
            else:
                form = my_div.div(line[1], class_='form-box')
                print_err(f'Form not created within section text', f'at {line}')
        except Exception as e:
            print_err({e}, f'form failed at {line}')
        return True
    # // end form carve out

    elif line[0] == 0:
        slug = my_div.p(line[1], class_='flush')
        return True
    elif line[0] == 'form':
        try:
            form.p(line[1], class_='form-box')
        except Exception as e:
            print_err({e}, f'attempted to add form from {line} to form box')
        return True
    elif str(line[0]).isnumeric():
        if line[0] == 1:
            return sub_levels(0, my_div, line)
        if 2 <= line[0] <= 5:
            return sub_levels(line[0]-1, subs_list[line[0]-2], line)


def sub_levels(depth, parent, data):   #  text, cls):
    global subs_list
    if in_bracs(data[1]) == start[depth]:
        try:
            subs_list[depth] = parent.ol(class_='lvl' + str(data[0]))
        except Exception as e:
            print_err(e, f'Couldn\'t add new depth {depth} for #{data[0]} for: {data[1]} at {data[2]}')
            return False
    try:
        subs_list[depth].li(data[1],title=str(data[2]))
        return True
    except Exception as e:
        print_err(e, f'Couldn\'t add {data[0]} with depth {depth} for: {data[2]}')
        return False


def write_html(html_doc):
    clean_doc = str(html_doc).replace('class_', 'class')  # clean up class tags
    bs_ors = BeautifulSoup(clean_doc, 'html.parser')
    pretty = bs_ors.prettify()
    pretty = pretty.replace('<bound method Tag.prettify of', '<!DOCTYPE html>')
    with open('new_html2.html', 'w') as writer:
        writer.write(pretty)
