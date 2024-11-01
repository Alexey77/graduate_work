import scrapy
import json
from urllib.parse import urlencode, quote
from datetime import datetime

from ..items import WikiPageItem


class RuWikiApiCrawlerSpider(scrapy.Spider):
    name = "ru_wiki_api_crawler"
    allowed_domains = ["ru.wikipedia.org"]
    categories = [
        "Категория:Фильмы",
        "Категория:Фильмы_по_алфавиту",
        "Категория:Кинорежиссёры_по_алфавиту",

        "Категория:Кинопродюсеры_по_алфавиту",
        "Категория:Кинопродюсеры_XX_века",
        "Категория:Кинопродюсеры_XXI_века",

        "Категория:Сценаристы_по_алфавиту",
        "Категория:Режиссёры-постановщики_по_алфавиту",
        "Категория:Кинооператоры_по_алфавиту",

        "Категория:Киноактёры_США",
        "Категория:Лауреаты_премии_BAFTA",
        "Категория:Лауреаты_премии_«Оскар»",
        "Категория:Актёры_XXI_века",
        "Категория:Актёры_XX_века",
        "Категория:Актёры_мыльных_опер_США",
        "Категория:Актёры_по_алфавиту",
        "Категория:Актёры_по_алфавиту",
        "Категория:Актёры_СССР",
        "Категория:Народные_артисты_РСФСР",
        "Категория:Заслуженные_артисты_РСФСР",
        "Категория:Народные_артисты_СССР",

        "Категория:Актрисы_по_алфавиту",
        "Категория:Актрисы_XX_века",
        "Категория:Актрисы_XXI_века",
    ]
    base_url = "https://ru.wikipedia.org/w/api.php"

    def start_requests(self):
        for category in self.categories:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'categorymembers',
                'cmtitle': category,
                'cmtype': 'subcat',
                'cmlimit': 'max'
            }
            url = f"{self.base_url}?{urlencode(params)}"
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        data = json.loads(response.body)

        # Обрабатываем текущую порцию категорий
        for member in data['query']['categorymembers']:
            if member['ns'] == 14:  # Namespace 14 is for categories
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'categorymembers',
                    'cmtitle': member['title'],
                    'cmtype': 'subcat|page',
                    'cmlimit': 'max'
                }
                url = f"{self.base_url}?{urlencode(params)}"
                yield scrapy.Request(url, callback=self.parse_subcategory)

        # Проверяем, есть ли в ответе параметр для пагинации
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

    def parse_subcategory(self, response):
        data = json.loads(response.body)
        for member in data['query']['categorymembers']:
            if member['ns'] == 0:  # Namespace 0 is for regular pages
                params = {
                    'action': 'parse',
                    'format': 'json',
                    'page': member['title'],
                    'prop': 'wikitext'
                }
                url = f"{self.base_url}?{urlencode(params)}"
                yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        data = json.loads(response.body)
        wikitext = data['parse']['wikitext']['*']
        title = data['parse']['title']

        item = WikiPageItem()
        item['wikitext'] = wikitext
        item['meta'] = {
            'title': title,
            'source': 'ru.wikipedia.org',
            'time_request': datetime.now().isoformat(),
            'url': response.url,
            'lang': 'ru'
        }
        yield item
