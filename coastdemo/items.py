# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CoastdemoItem(scrapy.Item):    
    code = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    designer = scrapy.Field()
    raw_color = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    sale_discount = scrapy.Field()
    link = scrapy.Field()
    type = scrapy.Field()
    gender = scrapy.Field()
    stock_status = scrapy.Field()
    skus = scrapy.Field()
    image_urls = scrapy.Field()
    
    pass
