'''
TODO:
    -> Google Docs -> Story -> Instagram
    -> Medium
    -> News Scrape -> Carousel -> Instagram
'''

import re
from termcolor import colored
from pathlib import Path

def extract_doc_id(url):
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    else:
        return None
    
def post_news():
    print("posted")