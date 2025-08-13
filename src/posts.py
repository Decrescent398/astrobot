'''
TODO:
    -> Google Docs -> Story -> Instagram
    -> Medium
    -> News Scrape -> Carousel -> Instagram
'''

import re

def extract_doc_id(url):
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    else:
        return None