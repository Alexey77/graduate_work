import scrapy


class WikiPageItem(scrapy.Item):
    title = scrapy.Field()
    wikitext = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    lang = scrapy.Field()
    revision_id = scrapy.Field()
    page_id = scrapy.Field()

    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    time_request = scrapy.Field()
