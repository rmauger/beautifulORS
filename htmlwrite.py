from html3 import HTML
from classify import in_bracs
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
    for line in ors_l[1:]:
        if line[0] == 'or_sec':
            try:
                sec_div = mn.div(id=line[1], class_='section')
            except:
                print(f'{line[1]} wasn\'t created correctly')
                sec_div = mn.div()
            ll = sec_div.p(line[1], class_='or_sec')
        elif line[0] == 'leadline':
            ll.span(' ' + line[1], class_='leadline')
        elif line[0] == 'slug':
            slug = sec_div.p(line[1], class_='slug')
        elif line[0] == 'source_note':
            sec_div.p(line[1], class_='source_note')
        elif line[0] == 'form_start':
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
                sec_div.p(line[1], class_='unknown')
            except Exception as e:
                print(f'err: {e}, found unclassified material outside of any section')
                mn.p(line[1], class_='unknown')
        elif line[0] == 'note_sec':
            sec_div.p(line[1], class_='note')
        elif line[0] == 'subtitle':
            mn.h3(line[1], class_='subtitle')

    # subsections:
        elif line[0] == 'subsec':
            if in_bracs(line[1]) == '1':
                ss = sec_div.ol(class_='subsec')
            try:
                ss.li(line[1]+' ')
            except:
                print(f'Subsection failed: Did not have associated section for {line[1]}')
        elif line[0] == 'para':
            if in_bracs(line[1]) == 'a':
                try:
                    pa = ss.ol('', class_='para')
                except:
                    print(f'error: could not add first paragraph of {line[1]}')
            try:
                pa.li(line[1] + ' ')
            except:
                print(f'error: did not add paragraph {in_bracs(line[1])} with {line[1]}')
        elif line[0] == 'subpara':
            if in_bracs(line[1]) == 'A':
                sp = pa.ol('', class_='subpara')
            try:
                sp.li(line[1] + ' ')
            except:
                print(f'error: did not add subparagraph {in_bracs(line[1])} with {line[1]}')
        elif line[0] == 'sub2para':
            if in_bracs(line[1]) == 'i':
                s2p = sp.ol('', class_='sub2para')
            try:
                s2p.li(line[1] + ' ')
            except Exception as e:
                print(f'err: {e}. Did not add sub2paragraph {in_bracs(line[1])} with {line[1]}')
        elif line[0] == 'sub3para':
            if in_bracs(line[1]) == 'I':
                s3p = s2p.ol('', class_='sub3para')
            try:
                s3p.li(line[1] + ' ')
            except Exception as e:
                print(f'err: {e}. Did not add sub3paragraph {in_bracs(line[1])} with {line[1]}')
        elif line[0] == 'index' or line[0] == 'index_sub':
            pass
        else:
            print(f'Did not print or classify {line}')
    write_html(h)


def write_html(html_doc):
    with open('new_html.html', 'w') as writer:
        writer.write('<!DOCTYPE html>')
        clean_doc = str(html_doc).replace('class_', 'class')    # clean up class tags
        writer.write(clean_doc)
