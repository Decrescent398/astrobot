import re, os, threading, time, json
import pyautogui as pg
from termcolor import colored
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def extract_doc_id(url):
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    else:
        return None

def post_news():
    
    pg.click(3438, 1050)

    n = 0
    article_path = r'C:\Users\hridd\Desktop\Docs\Codespace\Astrobot\data\out\articles'

    if len(os.listdir(article_path)) == 0:
        print(colored("Terminating function because news dir is empty", "green"))
        return

    for article in os.listdir(article_path):

        print(colored(f"Starting process for {article}", "green"))

        if n == 0:

            pg.hotkey('win')
            pg.write('edge')
            pg.press('enter')
            time.sleep(2)

            print(colored("Opened new Edge window", "green"))

        else:

            pg.hotkey('ctrl', 'l')
            pg.press('backspace')
            time.sleep(1)

            print(colored("Opened new Edge tab since window is already open", "green"))

        pg.hotkey('ctrl', 'l')
        time.sleep(0.5)
        pg.typewrite('https://www.instagram.com/')
        pg.press('enter')
        time.sleep(7)

        print(colored("Navigated to Instagram", "green"))

        pg.moveTo(2540, 889)
        pg.click()
        time.sleep(1)

        print(colored("Exited sleep mode pop up", "green"))

        pg.moveTo(1190, 550)
        pg.click()
        time.sleep(1)

        print(colored("Clicked Create Button", "green"))

        pg.moveTo(1173, 611)
        pg.click()
        time.sleep(1)

        print(colored("Clicked Post Button", "green"))

        pg.moveTo(2465, 850)
        pg.click()
        time.sleep(1)

        print(colored("Clicked on file upload button", "green"))

        pg.write(article_path)
        pg.press('enter')
        time.sleep(1)

        print(colored("Navigated to news directory", "green"))

        pg.click(1810, 333)

        print(colored("Clicked on top folder", "green"))

        loop = n

        while loop != 0:

            pg.press('down')
            loop -= 1

        print(colored("Navigated to required folder", "green"))

        pg.press('enter')
        time.sleep(1)

        print(colored("Entered required folder", "green"))

        pg.moveTo(1721, 550)
        pg.click()

        print(colored("Focused folder", "green"))

        pg.hotkey('ctrl', 'a')
        print(colored("Selected all items from folder", "green"))

        pg.press('enter')
        print(colored("Uploaded all items from folder", "green"))

        time.sleep(1)
        pg.moveTo(2970, 265)
        pg.click()

        print(colored("Clicked Next", "green"))

        time.sleep(1)
        pg.moveTo(3185, 265)
        pg.click()

        print(colored("clicked next on edit", "green"))

        time.sleep(1)
        pg.moveTo(2930, 425)
        pg.click()
        pg.write('Read our awesome astronomy blog please! (link in bio)')
        pg.press('enter')
        pg.press('enter')

        for i in range(0, 25):

            pg.write('.')
            pg.press('enter')

        pg.write('#viral #fyp #astronomy')

        print(colored("Finished typing bio", "green"))

        pg.moveTo(3185, 265)
        pg.click()
        time.sleep(15)

        print(colored("Finished posting", "green"))

        pg.hotkey('ctrl', 'shift', 'w')
        print(colored("Closed Edge window", "green"))

        n += 1

def read_article(doc_id):

    SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
    DOCUMENT_ID = doc_id
    CREDENTIALS_FILE = './credentials.json'
    TOKEN_FILE = './token.json'

    OUTPUT_FOLDER = Path("data/out/")
    METADATA_PATH = OUTPUT_FOLDER / "meta"

    creds_lock = threading.Lock()

    def get_credentials():

        with creds_lock:

            creds = None

            if os.path.exists(TOKEN_FILE):

                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

            if not creds or not creds.valid:

                if creds and creds.expired and creds.refresh_token:

                    creds.refresh(Request())

                else:

                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)

                with open(TOKEN_FILE, 'w') as token:

                    token.write(creds.to_json())

            return creds

    def read_google_doc(doc_id):

        creds = get_credentials()
        service = build('docs', 'v1', credentials=creds)
        doc = service.documents().get(documentId=doc_id).execute()

        content = doc.get('body').get('content')
        text_blocks = []

        for element in content:

            paragraph = element.get('paragraph')

            if not paragraph:

                continue

            heading = paragraph.get('paragraphStyle', {}).get('namedStyleType', '')
            elements = paragraph.get('elements', [])

            for index, elem in enumerate(elements):

                text_run = elem.get('textRun')
                inline_obj_id = elem.get("inlineObjectElement", {}).get("inlineObjectId")
                
                if text_run:

                    text = text_run.get('content', '').strip()
                    style = text_run.get('textStyle', {})
                    
                    if text:

                        run_info = {

                                    "type": {

                                            "item_type": "text",
                                            "heirarchy": None

                                        },

                                    "text": text,

                                    "styles": {
                                                "bold": False,
                                                "italic": False
                                            },

                                    "url": None,

                                    "alt_text": None

                                    }

                        if style.get('bold'):

                            run_info["styles"]["bold"] = True

                        else:

                            run_info["styles"]["bold"] = False

                        if style.get('italic'):

                            run_info["styles"]["italic"] = True

                        else:

                            run_info["styles"]["italic"] = False

                        if heading.startswith('HEADING_'):

                            run_info["type"]["item_type"] =  "text"
                            run_info["type"]["heirarchy"] =  "heading"

                        text_blocks.append(run_info)

                if inline_obj_id:

                    inline_obj = doc["inlineObjects"].get(inline_obj_id, {})
                    embedded_obj = inline_obj.get("inlineObjectProperties", {}).get("embeddedObject", {})
                    uri = embedded_obj.get("imageProperties", {}).get("contentUri")

                    if uri:

                        img_info = {

                                    "type": {

                                            "item_type": "image",
                                            "heirarchy": None

                                        },

                                    "text": None,

                                    "styles": {
                                                "bold": None,
                                                "italic": None
                                            },

                                    "url": uri,

                                    "alt_text": None

                                    }

                        text_blocks.append(img_info)

        print(colored(f"Finished Reading: {doc.get('title')}", "green"))
        
        index = 0
        
        while index < len(text_blocks):
                
            if text_blocks[index]["type"]["item_type"] == "image" and \
                text_blocks[index+1]["type"]["item_type"] == "text":
                    
                    text_blocks[index]["alt_text"] = text_blocks[index+1]["text"]
                    text_blocks.pop(index+1)
                    
            index+=1
                        
        with open(METADATA_PATH / f"doc-data-{len(os.listdir(METADATA_PATH))}.json", "w") as jf:

            json.dump(text_blocks, jf, indent=2)

        print(colored(f"Finished Saving: {doc.get('title')}", "green"))

    read_google_doc(DOCUMENT_ID)

def post_medium():

    OUTPUT_FOLDER = Path("data/out/")
    METADATA_PATH = OUTPUT_FOLDER / "meta"

    if len(os.listdir(METADATA_PATH)) == 0:
        print(colored("Terminating function because news dir is empty", "green"))
        return

    n = False
    for blog in os.listdir(METADATA_PATH):

        if blog.startswith('doc'):

            print(colored(f"Starting process for {blog}", "green"))

            with open(METADATA_PATH / blog, 'r') as jf: 
                blog_data = json.load(jf)

            if not n:

                pg.hotkey('win')
                pg.write('edge')
                pg.press('enter')
                time.sleep(2)

                print(colored("Opened new Edge window", "green"))

            else:

                pg.hotkey('ctrl', 'l')
                pg.press('backspace')
                time.sleep(1)

                print(colored("Opened new Edge tab since window is already open", "green"))

            pg.write("https://medium.com/me/stories/drafts")
            pg.press('enter')
            time.sleep(5)

            print(colored("Opened medium", "green"))

            pg.moveTo(2885, 280)
            pg.click()
            time.sleep(1)

            print(colored("Opened draft a story", "green"))

            pg.moveTo(2120, 290)
            pg.click()

            pg.write(blog_data[0]["text"])

            print(colored("Finished writing title", "green"))
            pg.press('enter')

            for item in blog_data[1:]:

                if item["type"]["item_type"] == "text" and \
                    item["type"]["heirarchy"] is None:

                    if item["styles"]["bold"] == True and \
                        item["styles"]["italic"] == True:

                        pg.hotkey("ctrl", "b")
                        pg.hotkey("ctrl", 'i')

                        pg.write(item["text"])

                        pg.hotkey("ctrl", "b")
                        pg.hotkey("ctrl", 'i')

                    elif item["styles"]["bold"] == False and \
                        item["styles"]["italic"] == True:

                        pg.hotkey("ctrl", 'i')

                        pg.write(item["text"])

                        pg.hotkey("ctrl", 'i')

                    elif item["styles"]["bold"] == True and \
                        item["styles"]["italic"] == False:

                        pg.hotkey("ctrl", 'i')

                        pg.write(item["text"])

                        pg.hotkey("ctrl", 'i')

                elif item["type"]["item_type"] == "text" and \
                    item["type"]["heirarchy"] is not None:

                    pg.press('enter')
                    pg.hotkey('ctrl', 'alt', '2')

                    if item["styles"]["bold"] == True and \
                        item["styles"]["italic"] == True:

                        pg.hotkey("ctrl", "b")
                        pg.hotkey("ctrl", 'i')

                        pg.write(item["text"])

                        pg.hotkey("ctrl", "b")
                        pg.hotkey("ctrl", 'i')


                    elif item["styles"]["bold"] == False and \
                        item["styles"]["italic"] == True:

                        pg.hotkey("ctrl", 'i')

                        pg.write(item["text"])

                        pg.hotkey("ctrl", 'i')

                    elif item["styles"]["bold"] == True and \
                        item["styles"]["italic"] == False:

                        pg.hotkey("ctrl", 'i')

                        pg.write(item["text"])

                        pg.hotkey("ctrl", 'i')

                    pg.hotkey('ctrl', 'alt', '2')
                    pg.press('enter')

                elif item["type"]["item_type"] == "image":

                    pg.press('enter')
                    x, y = pg.position()

                    pg.hotkey('ctrl', 't')
                    print(colored("Created new tab for image download", "green"))

                    pg.write(item["url"])
                    pg.press("enter")
                    time.sleep(5)

                    pg.hotkey('ctrl', 'w')
                    print(colored("Closed image tab after copying", "green"))

                    pg.moveTo(x, y)
                    pg.click()
                    pg.press('enter')

                    pg.write(item["alt_text"])
                    pg.press('enter')
                    print(colored("finished image and alt text", "green"))

            pg.moveTo(2875, 170)
            pg.click()
            print(colored("Clicked Publish on Medium", "green"))

            pg.moveTo(2695, 600)
            pg.click()
            print(colored("Entered textbox", "green"))

            pg.moveTo(1450, 250)

            pg.write("Astronomy")
            pg.press("down")
            pg.press("enter")

            pg.write("Astrophysics")
            pg.press("down")
            pg.press("enter")

            pg.write("Space")
            pg.press("down")
            pg.press("enter")

            pg.write("Universe")
            pg.press("down")
            pg.press("enter")

            pg.write("Science")
            pg.press("down")
            pg.press("down")
            pg.press("enter")

            print(colored("Entered hashtags", "green"))

            pg.moveTo(2663, 865)
            pg.click()
            print(colored("Finished publishing", "green"))

        n = True