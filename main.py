from ors_dl import *
from clean import *
from classify import *
from htmlwrite import *
from common import logger_list

chp = '90'
clean_ors = []


# Commented out pieces work, but no reason to keep downloading file
soup_ors = ors_html_dl(get_html(chp))     # strings from ORS <p> tags into raw unicode text

''' saving ORS raw download file'''
with open('ors_raw.txt', 'w') as raw:  # DEBUGGING
    raw.write(str(soup_ors))

first_clean = cleaner(soup_ors, chp)               # pass document through initial cleaner

''' saving ORS after first time through the cleaner'''
with open('ors_cln.txt', 'w') as cln:
    cln.write(first_clean)


for clean_line in first_clean.split('|'):               # first attempt to guess type after split based on pipes
    if len(str(clean_line).strip()) > 1:                             # for pieces longer than character
        clean_ors.append([typer(clean_line, chp), clean_line])      # add line & type to 2D list

''' saving ORS after first attempt at classification
for line in clean_ors:
    logger_list('clean1', line)
'''

reclassify(clean_ors, chp)
# todo put reclassify in separate module. Split into subfunctions?

''' saving ORS after 'reclassify' 
for line in clean_ors:
    logger_list('clean2', line)
'''

for delme in clean_ors:         # last cleanup, getting rid of any 0 char lines
    if len(delme[1]) <= 1 or (delme[1] == '_______________' and delme[0] != 'form'):
        print(f'deleted line for: {delme}')
        clean_ors.remove(delme)

# create function by which subsection can identify its history, add it to its mouseover?

''' saving ORS after final clean up
for line in clean_ors:
    logger_list('clean3' line)
'''

''' ***********************
# # Temp piece backward engineering 'clean_ors" from .txt
#
# with open('ors_typed.txt', 'r') as typed:
#     read = typed.readlines()
#
# clean_ors = []
#
# for i in read:
#     clean_ors.append(i[0:-1].split('|'))
'''

html_builder(clean_ors, chp)
