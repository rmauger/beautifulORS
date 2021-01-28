from bs4 import BeautifulSoup       # web scraper
from urllib import request
import re

# Extracts existing ORS chapter from Legislative URL & 'beautifies' it with beautiful soup.


def get_html(ors):
    ors_chp = str(ors).upper()   # TODO make function to call to get html for output.
    length = len(ors_chp)
    if ors_chp[-1] == 'A' or ors_chp[-1] == 'B' or ors_chp[-1] == 'C':  # don't count trailing A, B or C (e.g., ORS 72A)
        length -= 1
    ans = ors_chp
    for _ in range(3-length):
        ans = '0' + ans
    return fr'https://www.oregonlegislature.gov/bills_laws/ors/ors{ans}.html'


def ors_html_dl(ors_url):
    dl_ors = BeautifulSoup(request.urlopen(ors_url).read(), 'html.parser')  # TODO happy with parser? something easier?
    # dl_ors.smooth()    # depreciating at least temporarily. Not seeming to work on Pi.
    ors_line = ""
    for i in dl_ors.find_all('p', class_='MsoNormal'):          # extract line from html
        if re.search('align="center"', str(i)):
            if len(i.text.strip()) > 3:             # TODO wait, did any of this actually work/help?
                ors_line = ors_line + '|^' + i.text.strip()   # subtitles
        elif i.select('b'):         # leadlines
            ors_line = ors_line + '|' + i.text.strip()
        else:
            ors_line = ors_line + i.text
    return ors_line
