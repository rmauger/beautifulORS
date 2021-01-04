from bs4 import BeautifulSoup       # web scraper
from urllib import request
import re
import requests
import lxml

# Extracts existing ORS chapter from Legislative URL & 'beautifies' it with beautiful soup.

def ors_html_dl(ors):         # from ORS number, returns array for each line
    ors_chp = str(ors).upper()
    length = len(ors_chp)
    if ors_chp[-1] == 'A' or ors_chp[-1] == 'B' or ors_chp[-1] == 'C':  # don't count trailing A, B or C (e.g., ORS 72A)
        length -= 1
    ans = ors_chp
    for i in range(3-length):
        ans = '0' + ans
    ors_line = ""
    ors_url = fr'https://www.oregonlegislature.gov/bills_laws/ors/ors{ans}.html'
    dl_ors = BeautifulSoup(request.urlopen(ors_url).read(), 'html.parser')
    dl_ors.smooth()

    for i in dl_ors.find_all('p', class_='MsoNormal'):          # extract line from html
        if re.search('align="center"', str(i)):
            if len(i.text.strip()) > 3:
                ors_line = ors_line + '|^' + i.text.strip()   # subtitles
        elif i.select('b'):         # leadlines
            ors_line = ors_line + '|' + i.text.strip()   # TODO figure out leadlines for 9th time
        else:
            ors_line = ors_line + i.text
    return ors_line

    # with open(f'ORS_{chp}.txt', 'w') as ors:    # open up a txt file for writing
    #     for line in ors_line:
    #         ors.write(line[0] + '|' + str(line[1]))
