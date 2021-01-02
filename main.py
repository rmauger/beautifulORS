from ors_dl import *
from clean import *
from htmlwrite import *

chp = '99'
soup_ors = ors_html_dl(chp)     # strings from ORS <p> tags into raw unicode text
print(soup_ors.encode('utf-8'))
with open('ors_raw.txt', 'w') as raw:
    raw.write(soup_ors)

tempcount = 0
clean_ors = []

first_clean = cleaner(soup_ors, chp)               # pass document through initial cleaner
with open('ors_cln.txt', 'w') as cln:
    cln.write(first_clean)

for clean_line in first_clean.split('|'):      # first attempt to guess type after split based on pipes
#        print(clean_line)
    if len(clean_line) > 1:                # for pieces longer than character
        clean_ors.append([clean_line + hr, typer(clean_line, chp)]) # add line & type to 2D list

#print(clean_ors[45:50])

        # pass second clean into next step
        # ors_line.append([str(p_type_ors(j)), re.sub(r'#!', "", j + hr)]) # add piece & type to list

