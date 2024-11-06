import scrapy
from urllib.parse import urlencode
from scrapy_splash import SplashRequest
import re

class NaverSpider(scrapy.Spider):
    name = "naver"
    allowed_domains = ["naver.com"]

    def start_requests(self):
        search_keyword = getattr(self, 'keyword', 'Python')
        source = getattr(self, 'source', '블로그')
        num_articles = int(getattr(self, 'num_articles', 5))

        if source == "뉴스":
            url = f"https://search.naver.com/search.naver?where=news&query={search_keyword}"
            yield scrapy.Request(url, self.parse_news, meta={'num_articles': num_articles})
        elif source == "블로그":
            url = f"https://search.naver.com/search.naver?where=post&query={search_keyword}"
            yield scrapy.Request(url, self.parse_blog, meta={'num_articles': num_articles})
        elif source == "지식인":
            url = f"https://kin.naver.com/search/list.naver?query={search_keyword}"
            yield scrapy.Request(url, self.parse_knowledgein, meta={'num_articles': num_articles})

    def parse_news(self, response):
        articles = response.css('.news_tit')[:response.meta['num_articles']]
        for article in articles:
            title = article.attrib['title']
            link = article.attrib['href']
            # SplashRequest로 변경
            yield SplashRequest(link, self.parse_news_content, args={'wait': 2}, meta={'title': title})

    def parse_news_content(self, response):
        title = response.meta['title']
        
        # 다양한 본문 셀렉터 시도 (CSS 및 XPath)
        content_selectors = [
            "div#articleBodyContents *::text",    # 네이버 뉴스
            "div.content *::text",                # 예시1
            "div#articleBody *::text",            # 예시2
            "div.news_end *::text",               # 예시3
            "div.article_body *::text",           # 예시4
        ]
        
        content = ""
        for selector in content_selectors:
            content = response.css(selector).getall()
            if content:
                content = "\n".join(content).strip()
                break
        
        if not content:
            # XPath 방식 추가
            content_xpaths = [
                "//div[@id='articleBodyContents']//text()",
                "//div[contains(@class, 'content')]//text()",
                "//div[@id='articleBody']//text()",
                "//div[contains(@class, 'news_end')]//text()",
                "//div[contains(@class, 'article_body')]//text()",
            ]
            for xpath in content_xpaths:
                content = response.xpath(xpath).getall()
                if content:
                    content = "\n".join(content).strip()
                    break

        if content:
            # 광고, 공유 버튼 등의 불필요한 텍스트 정규식 필터링
            content = re.sub(r'\n+', '\n', content)  # 연속된 빈 줄 정리
            content = re.sub(r'\[.*?]\s+', '', content)  # [속보] 같은 텍스트 제거
            content = re.sub(r'광고\n+', '', content)  # 광고 텍스트 제거
            content = re.sub(r'\s*var .*?;', '', content)  # JavaScript 변수 제거
            content = re.sub(r'공유하기.*?\n', '', content)  # 공유하기 텍스트 제거
            content = re.sub(r'\s+', ' ', content)  # 연속된 공백을 하나의 공백으로
            content = re.sub(r'\n+', '\n', content)  # 연속된 줄바꿈을 하나로 줄임
            
        if not content:
            content = "내용을 불러올 수 없습니다."
            
        
        
       
        
        yield {
            'Title': title,
            'Content': content.strip()
        }

    def parse_blog(self, response):
        blogs = response.css('.api_txt_lines.total_tit')[:response.meta['num_articles']]
        for blog in blogs:
            title = blog.css('::text').get()
            link = blog.attrib['href']
            yield scrapy.Request(link, self.parse_blog_content, meta={'title': title})

    def parse_blog_content(self, response):
        title = response.meta['title']
        content = response.css('div.se-main-container *::text').getall()
        yield {
            'Title': title,
            'Content': "\n".join(content).strip()
        }

    def parse_knowledgein(self, response):
        questions = response.css('.basic1 > li > a')[:response.meta['num_articles']]
        for question in questions:
            title = question.css('::text').get()
            link = question.attrib['href']
            yield scrapy.Request(link, self.parse_knowledgein_content, meta={'title': title})

    def parse_knowledgein_content(self, response):
        title = response.meta['title']
        question_content = response.css('.c-heading__content::text').get()
        answers = response.css('.se-main-container *::text').getall()
        yield {
            'Title': title,
            'Question': question_content,
            'Answer': "\n".join(answers).strip()
        }
