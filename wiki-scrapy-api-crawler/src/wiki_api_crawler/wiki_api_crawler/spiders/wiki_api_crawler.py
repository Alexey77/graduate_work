import json
from enum import IntEnum
from urllib.parse import urlencode

import scrapy
from scrapy import signals
from ..settings import DB_URI
from ..database.wiki import WikiPageDatabaseManager
from ..items import WikiPageItem


class WikiNamespace(IntEnum):
    PAGE = 0
    CATEGORY = 14


class WikiApiCrawlerSpider(scrapy.Spider):
    name = "wiki_api_crawler"
    language = "ru"
    allowed_domains = [f"{language}.wikipedia.org"]
    categories = [
        # "Категория:Фильмы_России_1910_года", # для отладки маленькая категория
        "Категория:Кинематограф",
        "Категория:Киноактёры"
    ]
    skip_categories = ["Категория:Изображения"]
    base_url = f"https://{language}.wikipedia.org/w/api.php"

    def start_requests(self):
        for category in self.categories:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'categorymembers',
                'cmtitle': category,
                'cmtype': 'subcat|page',
                'cmlimit': 'max'
            }
            url = self.construct_url(params=params)
            yield scrapy.Request(url, callback=self.parse_category,
                                 meta={'category': category})

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_opened(self):

        self.db = WikiPageDatabaseManager(db_path=DB_URI)
        self.db.create_database()
        self.logger.info("The connection to the database is established")

    def spider_closed(self):

        if self.db:
            self.db.close()
            self.logger.info("The connection to the database is closed")

    def construct_url(self, params):
        return f"{self.base_url}?{urlencode(params)}"

    def parse_category(self, response):
        data = json.loads(response.body)

        for member in data['query']['categorymembers']:
            if member['ns'] == WikiNamespace.CATEGORY:
                skip_category = any(member['title'].startswith(skip_cat) for skip_cat in self.skip_categories)
                if skip_category:
                    continue

                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'categorymembers',
                    'cmtitle': member['title'],
                    'cmtype': 'subcat|page',
                    'cmlimit': 'max'
                }
                url = self.construct_url(params=params)
                yield scrapy.Request(url, callback=self.parse_category, meta={'category': member['title']})
            elif member['ns'] == WikiNamespace.PAGE:
                params = {
                    'action': 'parse',
                    'format': 'json',
                    'page': member['title'],
                    'prop': 'wikitext'
                }
                url = self.construct_url(params=params)
                yield scrapy.Request(url, callback=self.parse_page)

        if 'continue' in data:
            cmcontinue = data['continue']['cmcontinue']
            category = response.meta['category']
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'categorymembers',
                'cmtitle': category,
                'cmtype': 'subcat',
                'cmlimit': 'max',
                'cmcontinue': cmcontinue
            }
            url = self.construct_url(params=params)
            yield scrapy.Request(url, callback=self.parse_category, meta={'category': category})

    def parse_page(self, response):
        data = json.loads(response.body)
        page_id = data['parse']['pageid']

        item = WikiPageItem(
            title=data['parse']['title'],
            wikitext=data['parse']['wikitext']['*'],
            url=response.url,
            page_id=data['parse']['pageid']
        )

        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "ids",
            "format": "json",
            "pageids": page_id
        }
        api_url = self.construct_url(params)

        yield scrapy.Request(api_url, callback=self.parse_page_revision, meta={'item': item})

    def parse_page_revision(self, response):
        item = response.meta['item']
        data = json.loads(response.text)

        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "revisions" in page:
                item["revision_id"] = page["revisions"][0]["revid"]
                break
        else:
            self.logger.warning(f"No revision ID found for page with id {item['page_id']}")

        yield item
