import scrapy
import datetime, re, json

class NewsScraper(scrapy.Spider):
    name = 'particle'
    start_urls = ['https://particle.news/topic/45H-Zo-Nel']

    def parse(self, response):
        for topic in response.css('div.topic'):
            for subtopic in topic.css('p.subtopics'):
                subtopics = subtopic.css('a::attr(href)').getall()

                subtopic_links = ["https://particle.news" + extracted_subtopic for extracted_subtopic in subtopics]

                for link in subtopic_links:
                    yield response.follow(link, callback=self.parse_subtopics)

    def parse_subtopics(self, response):
        for article in response.css('ul.top-stories'):
                    individual_article_links = article.css('a::attr(href)').getall()

                    article_links = ["https://particle.news" + extracted_link for extracted_link in individual_article_links]

                    for link in article_links:
                        yield response.follow(link, callback=self.parse_news)

    def parse_news(self, response):
        data = []
        for items in response.css('div.container'):
            data.append(
            {
            'title': [re.sub(r'[\/:*?"<>|]', '_', title) for title in items.css('div.cluster-headline h1').xpath('normalize-space(.)').getall()],
            'points': items.css('ul li').xpath('normalize-space(.)').getall(),
            'image-links': [svg.attrib['xlink:href'] for svg in items.css('svg.image-pile g image')]
            }
            )
        with open(f"./data/out/meta/news-output-{datetime.date.today()}.json", 'a') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')