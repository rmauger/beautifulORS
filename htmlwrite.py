from html3 import HTML
from classify import in_bracs
from bs4 import BeautifulSoup
import re

def html_builder(ors_l, ors):
    h = HTML(newlines=True)
    ht = h.html(lang="en-US", newlines=True)
    hd = ht.head(newlines=True)
    hd.link(rel='stylesheet', href='orsstyle.css')
    hd.title(ors_l[0][1])
    by = ht.body(newlines=True)
    by.h1(ors_l[0][1], class_='title')

    # build out index
    ix = by.div(class_='toc', id='chp_' + str(ors) + '_index')
    ix.h2('Table of Contents')
    ix_list = None
    for ix_line in ors_l[1:]:
        if ix_line[0] == 'index_sub':
            ix.h3(ix_line[1])
            ix_list = ix.ul(' ')
        if ix_line[0] == 'index':
            if ix_list is None:
                ix_list = ix.ul(' ')
            if re.match(fr'^{ors}\.\d{{3}}', ix_line[1]):
                ul_ix = ix_list.li
                ul_ix.a(ix_line[1], href='#'+(ix_line[1]))
            else:
                ul_ix.span(' ' + ix_line[1])  # Leadline
    # build out main content:
    mn = by.div(class_='main')
    mn.h2('Oregon Revised Statutes', class_='subtitle')
    err = None
    for line in ors_l[1:]:
        if line[0] == 'or_sec':
            sec_div = mn.div(id=line[1], class_='section')
            ll = sec_div.p(line[1], class_='or_sec')
            err = None
        elif line[0] == 'da_sec':
            # try:
            sec_div = mn.div(class_='section alternate')
            # except:
            #     print(f'{line[1]} wasn\'t created correctly')
            #     sec_div = mn.div(class_='section alternate')
            sec_div.p(line[1], class_='or_sec')
        elif line[0] == 'leadline':
            ll.span(' ' + line[1], class_='leadline')
        elif line[0] == 'slug':
            slug = sec_div.p(line[1], class_='slug')
        elif line[0] == 'source_note':
            sec_div.p(line[1], class_='source_note')
        elif line[0] == 'form_start':           # trying to create new form box based on parentage
            try:
                form_id = line[2]
                if form_id == 'slug':
                    form = slug.div(class_='form-box')
                elif form_id == 'subsec':
                    form = ss.div(class_='form-box')
                elif form_id == 'para':
                    form = pa.div(class_='form-box')
                elif form_id == 'subpara':
                    form = sp.div(class_='form-box')
                elif form_id == 'sub2para':
                    form = s2p.div(class_='form-box')
                elif form_id == 'sub3para':
                    form = s3p.div(class_='form-box')
                else:
                    form = sec_div.div(line[1], class_='form-box')
                    print(f'Err. form created within section, but not within text of section for {line}')
            except Exception as e:
                print(f'Form fail: {e} for :{line}')
                form = mn.form.div(class_='form-box')
        elif line[0] == 'form':
            try:
                form.p(line[1], class_='form-box')
            except Exception as e:
                print(f'ERR: {e}, could not add line --{line}--to existing form box')
                mn.p(line[1], class_='form-box')
        elif line[0] == 'dunno':
            try:
                if err is None:
                    err = sec_div.div(class_='unknown')
                    err.p("** WARNING ** ", style='font-weight:bold;;text-align:center')
                    err.p("Lines below are part of this section, but may not have parsed correctly.", \
                                style='font-weight:bold; text-align: center')
                    ptemp = err.p("View original from the ", \
                                style='font-weight:bold:;text-align: center; margin-bottom: 20px')
                    ptemp.a('Oregon Legislature Website', \
                                href='https://www.oregonlegislature.gov/bills_laws/Pages/ORS.aspx')
                    ptemp += '.'
            except Exception as e:
                print(f'err: {e}, error message did not generate for {line}')
            try:
                err.p(line[1])
            except Exception as e:
                print(f'err: {e}, error message did not generate for {line}')
                mn.p(line[1], class_='unknown')
        elif line[0] == 'note_prev':
            sec_div.p(line[1], class_='note')
        elif line[0] == 'note_next' or line[0] == 'note_both':
            sec_div = mn.div('')
            sec_div.p(line[1], class_='note')
        elif line[0] == 'subtitle':
            mn.h3(line[1], class_='subtitle')
        elif line[0] == 'sub2title':
            mn.h4(line[1], class_='sub2title')
    # subsections:
        elif line[0] == 'subsec':
            if in_bracs(line[1]) == '1':
                ss = sec_div.ol(class_='subsec')
            try:
                ss.li(line[1]+' ')
            except Exception as e:
                print(f'Err: {e} html failed for: {line}')
        elif line[0] == 'para':
            if in_bracs(line[1]) == 'a':
                pa = ss.ol('', class_='para')
            try:
                pa.li(line[1] + ' ')
            except Exception as e:
                print(f'Err: {e} html failed for: {line}')
        elif line[0] == 'subpara':
            if in_bracs(line[1]) == 'A':
                sp = pa.ol('', class_='subpara')
            try:
                sp.li(line[1] + ' ')
            except Exception as e:
                print(f'Err: {e} html failed for: {line}')
        elif line[0] == 'sub2para':
            if in_bracs(line[1]) == 'i':
                s2p = sp.ol('', class_='sub2para')
            try:
                s2p.li(line[1] + ' ')
            except Exception as e:
                print(f'Err: {e} html failed for: {line}')
        elif line[0] == 'sub3para':
            if in_bracs(line[1]) == 'I':
                s3p = s2p.ol('', class_='sub3para')
            try:
                s3p.li(line[1] + ' ')
            except Exception as e:
                print(f'Err: {e} html failed for: {line}')
        elif line[0] == 'index' or line[0] == 'index_sub':
            pass
        else:
            print(f'Did not print or classify {line}')
    write_html(h)


def write_html(html_doc):
    clean_doc = str(html_doc).replace('class_', 'class')  # clean up class tags
    pretty = str(BeautifulSoup(clean_doc, 'html.parser').prettify)
    pretty = pretty.replace('<bound method Tag.prettify of', '<!DOCTYPE html>')
    with open('new_html.html', 'w') as writer:
        writer.write(pretty)
