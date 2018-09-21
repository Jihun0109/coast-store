# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor
from pyquery import PyQuery as PQ
import re

from coastdemo.items import CoastdemoItem

#######################################################################
#                                                                     #
#        CoastSpider Class  (base on CrawlSpider)                     #
#                                                                     #
#######################################################################

class CoastSpider(CrawlSpider):
    name = 'coast'
    allowed_domains = ['coast-stores.com']
    start_urls  = [
    				'https://www.coast-stores.com',
    ]

    rules = (
        Rule(LinkExtractor(         # Rule for extracting and following category links.
                allow='/c/',
                deny=['filter','sort','c/all','c/new-in'],
            ),  callback='parse_categories'),
    )

    #####################################################################
    # Return:   'A' for apparel
    #           'S' for shoes
    #           'B' for bags
    #           'J' for jewelry
    #           'R' for accessories
    # parse link string and returns type character.
    def get_type_by_category_link(self, category_link):
        print category_link
        if 'jewell' in category_link:
            return u'J'
        elif 'bags' in category_link:
            return u'B'
        elif 'shoes' in category_link:
            return u'S'
        elif ('scarves' in category_link) or ('bags' in category_link) or ('faux' in category_link):
            return u'R'
        else:
            return u'A'

    #####################################################################
    # parse sub-category pages and request for every product links.
    def parse_categories(self, response):
        prod_type = self.get_type_by_category_link(response.url)
        
        prod_links = LinkExtractor(allow='/p/').extract_links(response)
        for link in prod_links:            
            yield Request(
                           link.url,
                           callback=self.parse_item,
                           meta={'prod_type':prod_type}
                          )
        
    ####################################################################
    # callback function to process product page and yield item
    def parse_item(self, response):
        # Read DOM.
        doc = PQ(response.body) 

        # Price info in list variable. There is 2 kinds of price - standard and sales.
        prices    = re.findall('[\d.,]+', doc('p[itemprop="offers"]').text())

        # Currency info - extracted from the raw html text because it is not in the dom tree.
        currency  = re.findall(r'config.currentCurrency\s*=\s*\"(\w+)\"', response.body)

        # Options to get stock information
        options   = doc('.option-size > ul > li > a')
        
        item  = CoastdemoItem()

        item['code']            = response.url.split('/')[-1]        
        item['name']            = PQ(doc('meta[itemprop="name"]')).attr('content').title()
        item['description']     = PQ(doc('meta[itemprop="description"]')).attr('content')
        item['designer']        = u'Coast' # Not Exsit. So Set To Default Value
        item['raw_color']       = doc('li.active > span').text()
        item['price']           = "%.2f" % float(prices[0])
        item['currency']        = currency[0] if currency else "GBP" 
        item['sale_discount']   = item['price'] if len(prices) < 2 else "%.2f" % float(prices[1])
        item['link']            = response.url        
        item['type']            = response.meta['prod_type']
        item['gender']          = u"F" # The website has only women's goods.
        
        item['stock_status']    = {}        
        for opt in options:            
            item['stock_status'][opt.text] = not(PQ(opt).parents('li').attr('class') == "no-stock")

        item['skus']            = PQ(doc('meta[name="keywords"]')).attr('content').split(",")
        item['image_urls']      = [PQ(img).attr('src') for img in doc('.prod-image > div img')]
        
        yield item

    