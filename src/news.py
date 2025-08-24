import requests, os, shutil, datetime, json, re, sys
import PIL
import asyncio
import subprocess
import urllib.request
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from pathlib import Path
from termcolor import colored
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy.utils.defer import ensureDeferred
from twisted.internet import asyncioreactor
from twisted.internet import defer
from particlescraper.particlescraper.spiders.newsscraper import NewsScraper

# Output directory paths
OUTPUT_FOLDER = Path("data/out/")
METADATA_PATH = OUTPUT_FOLDER / "meta"
ARTICLE_DATA_PATH = OUTPUT_FOLDER / "articles"
PARTICLE_IMAGE_ASSET = Path("C:/Users/hridd/Desktop/Docs/Codespace/Astrobot/assets/poweredbyparticle.png")

async def news():
    
    # Clean old JSON files
    if len(os.listdir(METADATA_PATH)) >= 1:
        for json_file in os.listdir(METADATA_PATH):
            os.remove(METADATA_PATH / json_file)
    
    # Clean old article directories
    if len(os.listdir(ARTICLE_DATA_PATH)) >= 1:
        for article_dir in os.listdir(ARTICLE_DATA_PATH):
            shutil.rmtree(ARTICLE_DATA_PATH / article_dir)
    
    yesterday_date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d %b %Y")

    """Main news function that starts news scraping."""
    # crawler_process = CrawlerProcess(get_project_settings())
    # crawler_process.crawl(NewsScraper)
    # crawler_process.start()
    
    await asyncio.to_thread(
        subprocess.run,
        [sys.executable, "-m", "scrapy", "crawl", "particle"],
        cwd="C:/Users/hridd/Desktop/Docs/Codespace/Astrobot/particlescraper",
        check=True
    )

    print(colored(f"News files from {yesterday_date} deleted", "green"))
    print(colored("Started news", "green"))
    # Start news scraping process
    clean_data()
    print(colored("Started news", "green"))

def clean_data():

    """Clean and organize article data, download images, and create content files."""

    news_articles = []

    today_date = datetime.date.today()
    json_filename = f"news-output-{today_date}.json"
    
    try:
        with open(METADATA_PATH / json_filename) as json_file:
            for line in json_file:
                news_articles.append(json.loads(line))
    except FileNotFoundError:
        return

    def download_image(image_url, image_name, article_folder):

        """Download an image from URL to specified folder."""
        request_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        image_request = urllib.request.Request(image_url, headers=request_headers)
        
        try:

            with urllib.request.urlopen(image_request, timeout=10) as response:

                if image_name.endswith("-icon"):
                    image_path = ARTICLE_DATA_PATH / article_folder / f"{image_name}.png"

                else:
                    image_path = ARTICLE_DATA_PATH / article_folder / f"{image_name}.png"

                with open(image_path, 'wb') as image_file:
                    image_file.write(response.read())

        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:

            print(colored(f"Error occurred {error} while downloading {image_url}", "red"))

    print(colored("Starting clean", "green"))

    for article in news_articles:

        image_index = 0

        try:
            article_folder_path = ARTICLE_DATA_PATH / article["title"][0]
            os.mkdir(article_folder_path)

        except FileExistsError:
            continue
        
        # Write article content to file
        content_file_path = article_folder_path / "content.txt"

        with open(content_file_path, 'a') as content_file:
            content_file.write(article["title"][0]+'\n')

            for content_line in article["points"]:
                try:
                    content_file.write(content_line + '\n')
                except UnicodeEncodeError:
                    pass

        # Download images for this article
        for image_link in article["image-links"]:
            image_name = f"{image_index}"

            if image_index % 2 != 0:
                image_name += "-icon"

            download_image(image_link, image_name, article["title"][0])
            image_index += 1
    
    print(colored("Finished clean", "green"))
    
    make_slides()

def make_slides():

    for article_dir in os.listdir(ARTICLE_DATA_PATH):
        dirs = os.listdir(ARTICLE_DATA_PATH / article_dir)

        for index, item in enumerate(dirs):

            try:
                filepath = ARTICLE_DATA_PATH / f"{article_dir}/{item}"
            except FileNotFoundError as e:
                continue

            try:
                next_fp = ARTICLE_DATA_PATH / f"{article_dir}/{dirs[index+1]}"
            except (IndexError, FileNotFoundError) as e:
                pass

            if "icon" not in item:

                try:
                    img = Image.open(filepath)
                except PIL.UnidentifiedImageError as e: #Skipping through content.txt files
                    continue

                width, height = img.size
                if width > height:
                    box = (int((width - height) / 2), 0, int((width + height) / 2), height)

                elif height > width:
                    box = (0, int((height - width) / 2), width, int((height + width) / 2))

                else: #When image is already a square
                    box = (0, 0, width, height)

                img = img.crop(box)

                try:
                    if "icon" in dirs[index+1]:
                        ico = Image.open(next_fp)
                        ico = ico.resize((48,48))
                        box = (8, 8, 56, 56)
                        img.paste(ico, box)

                except (IndexError, FileNotFoundError, PIL.UnidentifiedImageError):
                    pass

                img = img.resize((1080, 1080))
                blur_box = img.crop((0, 810, 1080, 1080)) #Blurring bottom quarter
                blur_region = blur_box.filter(ImageFilter.GaussianBlur(radius=5))
                img.paste(blur_region, (0, 810, 1080, 1080))
                img.save(filepath, "PNG")

    print(colored(f"Finished icon overlay and blur", "green"))

    for article_dir in os.listdir(ARTICLE_DATA_PATH):

        for item in os.listdir(ARTICLE_DATA_PATH / article_dir):

            if "icon" in item:

                os.remove(ARTICLE_DATA_PATH / article_dir / item)
    
    print(colored("Deleted extra icons", "green"))

    for article_dir in os.listdir(ARTICLE_DATA_PATH):

        if len(os.listdir(ARTICLE_DATA_PATH / article_dir)) != 7:

            loop = 7 - len(os.listdir(ARTICLE_DATA_PATH / article_dir))

            while loop != 0:

                blank = Image.new('RGBA', (1080, 1080), color='black')
                blank.save(ARTICLE_DATA_PATH / article_dir / f'{7-loop}-blank.png')
                loop -= 1
    
    print(colored("Created blanks", "green"))

    def get_font(font_size=36):
        return ImageFont.truetype("fonts/Libre_Baskerville/LibreBaskerville-Bold.ttf", font_size) #37px length per line, width = 22px (0.6*font lenght estimate)

    for article_dir in os.listdir(ARTICLE_DATA_PATH):

        f = open(ARTICLE_DATA_PATH / article_dir / "content.txt", 'r')
        f.seek(0)

        all_lines = [line for line in f.readlines() if line.strip()] #Ignores last line which is empty
        image_dir = os.listdir(ARTICLE_DATA_PATH / article_dir)
        image_dir.remove('content.txt') #We don't want PIL to process content.txt as an image
        index = 0
        
        shutil.copy(PARTICLE_IMAGE_ASSET, ARTICLE_DATA_PATH / article_dir / "final-7-particle-icon.png")

        for image, line in zip(image_dir, all_lines):
            
            index += 1 #Only for final naming purposes doesn't do anything else

            try:
                os.rename(ARTICLE_DATA_PATH / article_dir / image, ARTICLE_DATA_PATH / article_dir / f"final-{index}.png")
                img = Image.open(ARTICLE_DATA_PATH / article_dir / f"final-{index}.png")

            except (PIL.UnidentifiedImageError, FileNotFoundError, PIL.Image.DecompressionBombError, OSError) as e:
                continue

            def write_text(y, line, image):
                
                x = 20 #20px padding gap so it's not congested as hell
                start_newline = 0

                drw = ImageDraw.Draw(img)

                line = line.replace('\n', '') 

                while start_newline < len(line):
                    
                    #46 max chars (40px+40px padding, 1000 box-space/ 22px width per letter)

                    if len(line[start_newline:start_newline+46].split(' ')[:-1]) > 1:
                        threshold = line[start_newline:start_newline+46].split(' ')[:-1] #Picks all words except the last one, incase it might have been chopped off

                    elif len(line[start_newline:start_newline+46].split(' ')[:-1]) == 1: #If the list has only 2 pick all of them
                        threshold = line[start_newline:start_newline+46].split(' ')

                    else:
                        print(line)
                        break
                    
                    this_line = " ".join(threshold)
                    x_offset = int((1080 - (len(this_line) * 22))/2)
                    drw.text((x+x_offset, y), this_line, font=get_font(), spacing=4)

                    start_newline += len(this_line)
                    y += 37
                
                img.save(ARTICLE_DATA_PATH / article_dir / f"final-{index}.png")

            if "blank" in image:

                write_text(y=540, line=line, image=img)
                
            else:

                write_text(y=810, line=line, image=img)

        f.close()

    print(colored("Finished text overlay", "green"))
