from bs4 import BeautifulSoup       # web scraper
from urllib import request
import requests
import lxml

# Extracts existing ORS chapter from Legislative URL & 'beautifies' it with beautiful soup.


def ors_html_dl(ors):         # from ORS number, returns array for each line
    ors_chp = str(ors).upper()
    length = len(ors_chp)
    print(ors_chp[-1])
    if ors_chp[-1] == 'A' or ors_chp[-1] == 'B' or ors_chp[-1] == 'C':
        length -= 1
    ans = ors_chp
    for i in range(3-length):
        ans = '0' + ans
    ors_line = ""
    ors_url = fr'https://www.oregonlegislature.gov/bills_laws/ors/ors{ans}.html'
    #rq_ors = BeautifulSoup(requests.get(ors_url).content, 'lxml')
    dl_ors = BeautifulSoup(request.urlopen(ors_url).read(), 'html.parser')

    for i in dl_ors.find_all('p', class_='MsoNormal', align='center'):          # extract line from html
        print(i)
        ors_line = ors_line + i.text
        try:
            print(i.find('b').text)
        except:
            pass
        try:
            print(i.find('p').text) # , style='margin-top:0in;margin-right:0in;margin-bottom:0in;margin-left:.75in;margin-bottom'
                                    # ':.0001pt;text-align:center;text-indent:-.75in;line-height:normal;text-autospace'
                                    # ':none'))
        except:
            pass
    return ors_line

    # with open(f'ORS_{chp}.txt', 'w') as ors:    # open up a txt file for writing
    #     for line in ors_line:
    #         ors.write(line[0] + '|' + str(line[1]))
