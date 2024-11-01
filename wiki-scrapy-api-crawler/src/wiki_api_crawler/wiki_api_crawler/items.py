import scrapy


class WikiPageItem(scrapy.Item):
    wikitext = scrapy.Field()
    meta = scrapy.Field()
