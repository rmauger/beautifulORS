from html3 import HTML

h = HTML(newlines=True)

ht = h.html(lang="en-US", newlines=True)
head = ht.head(newlines=True)

# for i in txt.readlines():
# title=head.title('The Page Title')
# st=head.style(r'body {font-family:veranda; color:rgb(60, 0, 40);} h1 {background-color:blue;} h2 {'
#               r'background-color:green;}')
# by=ht.body(newlines=True)
#
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
# print(h)

with open('new_html.html', 'w') as writer:
    writer.write('<!DOCTYPE html>')
    writer.write(str(h))