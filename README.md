# beautifulORS
Download, parses and recreates website for Oregon Revised Statutes.

The purpose is basically just experimenting with some coding & github. I don't know how you found this but prepare to be underwhelmed. Even if you're really into Oregon Laws.

Python downloads ORS chapter from Oregon Legislature Website.
Beautiful Soup helps to scrape website to find paragraphs.
Based on paragraph content (regex), tries to classify the paragraphs.
Uses python html3 to convert to new html file which uses local css file.

Needed Libraries (maybe built-in?): re, bs4, urllib, 
