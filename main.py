from ors_dl import *
from clean import *
from classify import *
from htmlwrite import *

chp = '93'

# Commented out pieces work, but no reason to keep downloading file, seems a bit suspect
soup_ors = ors_html_dl(chp)     # strings from ORS <p> tags into raw unicode text

with open('ors_raw.txt', 'w') as raw:  # DEBUGGING
     raw.write(str(soup_ors))

first_clean = cleaner(soup_ors, chp)               # pass document through initial cleaner

with open('ors_cln.txt', 'w') as cln:  # DEBUGGING
    cln.write(first_clean)

clean_ors = []
for clean_line in first_clean.split('|'):               # first attempt to guess type after split based on pipes
    if len(str(clean_line).strip()) > 1:                             # for pieces longer than character
        clean_ors.append([typer(clean_line, chp), clean_line])      # add line & type to 2D list

reclassify(clean_ors)

with open('ors_typed.txt', 'w') as typed:
    for i in clean_ors:
        typed.write(f'{i[0]}|{i[1]}\n')
# ***********************


# # Temp piece backward engineering 'clean_ors" from .txt
#
# with open('ors_typed.txt', 'r') as typed:
#     read = typed.readlines()
#
# clean_ors = []
#
# for i in read:
#     clean_ors.append(i[0:-1].split('|'))


html_builder(clean_ors, chp)
