from html3 import HTML


def html_builder(ors_l, ors):
    count = 0
    div_list = []
    h = HTML(newlines=True)
    ht = h.html(lang="en-US", newlines=True)
    hd = ht.head(newlines=True)
    hd.link(rel='stylesheet', href='orsstyle.css')
    hd.title(ors_l[0][1])
    by = ht.body(newlines=True)
    by.h1(ors_l[0][1], class_='Title')

    # build out index
    ix = by.div(class_='toc', id='ors_' + str(ors) + '_index')
    ix.h2('Table of Contents')
    ix_list = ix.ul
    ix_count = True
    for ix_line in ors_l:
        if ix_line[0] == 'index':
            if ix_count:
                ul_ix = ix_list.li # (class_='toca')
                ul_ix.a(ix_line[1], class_='toca', href='#'+(ix_line[1]))
            else:
                try:
                    ul_ix.span(' ' + ix_line[1])
                except:
                    print(f'did not add {ix_line[1]} info to index list')
            ix_count = not ix_count

    # build out main content:
    mn = by.div(class_='main')
    for line in ors_l:
        if line[0] == 'or_sec':
            try:
                div_list.append(mn.div(id=line[1], class_='section'))
            except:
                print(f'{line[1]} wasn\'t created correctly')
                div_list.append(mn.div())
            ll = div_list[count].p(line[1], class_='or_sec')
            count += 1
        if line[0] == 'leadline':
            ll.span(' '+ line[1], class_='leadline')
        if line[0] == 'slug':
            div_list[count-1].p(line[1], class_='slug')
        if line[0] == 'source_note':
            div_list[count - 1].p(line[1], class_='source_note')
        if line[0] == 'dunno':
            div_list[count - 1].p(line[1], class_='unknown')
        if line[0] == 'note':
            mn.p(line[1], class_='note')
        if line[0] == 'subtitle':
            mn.h3(line[1], class_='subtitle')
    # t = by.table(border='.5', newlines=True)
    # for i in range(2, 11, 2):
    #     r = t.tr
    #     r.td(f'column # {i}')
    #     r.td(f'squared {i**2}')
    # t = by.table(border='.3')
    # r = t.tr
    # r.td('blahblah')
    # r = t.tr
    # r.td('more blah')
    # by.p('Hello World')
    # by.p('Goodbye World')
    #

    write_html(h)


def write_html(html_doc):
    with open('new_html.html', 'w') as writer:
        writer.write('<!DOCTYPE html>')
        clean_doc = str(html_doc).replace('class_', 'class')
        str(html_doc)
        writer.write(clean_doc)
