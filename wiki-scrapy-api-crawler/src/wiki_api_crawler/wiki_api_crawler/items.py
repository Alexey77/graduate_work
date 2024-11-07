import scrapy


class WikiPageItem(scrapy.Item):
    title = scrapy.Field()
    wikitext = scrapy.Field()
    url = scrapy.Field()
    revision_id = scrapy.Field()
    page_id = scrapy.Field()
    meta = scrapy.Field()
