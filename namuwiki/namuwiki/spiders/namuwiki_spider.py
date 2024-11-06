import scrapy

class NamuwikiSpider(scrapy.Spider):
    name = "namuwiki"

    def __init__(self, search_term=None, **kwargs):
        super().__init__(**kwargs)
        self.search_term = search_term

    def start_requests(self):
        search_url = f"https://namu.wiki/w/{self.search_term}"
        yield scrapy.Request(url=search_url, callback=self.parse)

    def parse(self, response):
        title = response.css('h1::text').get()
        content = response.css('div.wiki-inner-content').getall()
        content_text = "\n".join(content)
        
        yield {
            'Title': title,
            'Content': content_text
        }