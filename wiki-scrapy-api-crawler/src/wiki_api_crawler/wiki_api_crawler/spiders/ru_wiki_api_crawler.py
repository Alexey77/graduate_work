import scrapy
import json
from enum import IntEnum
from datetime import datetime
from urllib.parse import urlencode

from ..items import WikiPageItem


class WikiNamespace(IntEnum):
    PAGE = 0
    CATEGORY = 14


class RuWikiApiCrawlerSpider(scrapy.Spider):
    name = "ru_wiki_api_crawler"
    allowed_domains = ["ru.wikipedia.org"]
    categories = [
        "Категория:Кинематограф",
        "Категория:Киноактёры"
    ]
    skip_categories = ["Категория:Изображения"]
    base_url = "https://ru.wikipedia.org/w/api.php"

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
            url = f"{self.base_url}?{urlencode(params)}"
            yield scrapy.Request(url, callback=self.parse_category, meta={'category': category})

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
                url = f"{self.base_url}?{urlencode(params)}"
                yield scrapy.Request(url, callback=self.parse_category, meta={'category': member['title']})
            elif member['ns'] == WikiNamespace.PAGE:
                params = {
                    'action': 'parse',
                    'format': 'json',
                    'page': member['title'],
                    'prop': 'wikitext'
                }
                url = f"{self.base_url}?{urlencode(params)}"
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
            url = f"{self.base_url}?{urlencode(params)}"
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
        item['meta'] = {
            'source': 'ru.wikipedia.org',
            'time_request': datetime.now().isoformat(),
            'lang': 'ru'
        }

        api_url = f"https://ru.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=ids&format=json&pageids={page_id}"

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
