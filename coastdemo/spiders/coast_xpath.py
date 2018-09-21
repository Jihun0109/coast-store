# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Request
from scrapy.linkextractors import LinkExtractor
import re

from coastdemo.items import CoastdemoItem

#######################################################################
#                                                                     #
#        CoastSpider Class  (base on CrawlSpider)                     #
#                                                                     #
#######################################################################

class CoastSpider(CrawlSpider):
    name = 'coast_xpath'
    allowed_domains = ['www.coast-stores.com']
    start_urls = [
    				'https://www.coast-stores.com/',
    ]

    #######################################################################
    # Parse first landing page and select sub categories except for "All ~ " sub categories. 
    def parse(self, response):    	
    	categories = response.xpath('//a[contains(@class,"2-list_")][not(contains(@href, "all"))]')
    	for cate in categories:
    		category_title    = cate.xpath('./text()').extract_first()
    		category_link     = cate.xpath('./@href').extract_first()
    		
    		yield Request(
                            response.urljoin(category_link), 
                            self.parse_category, 
                            meta={'category':category_title}
                            )
    		
    #######################################################################
	# Callback to process category selection
    def parse_category(self, response):
    	prod_links = response.xpath('//a[@class="product-block__image"]/@href').extract()

    	for link in prod_links:            
            yield Request(
                            response.urljoin(link), 
                            self.parse_item, 
                            meta={'category':response.meta['category']}
                            )

    	# Case in pagination
    	next_links = response.xpath('//a[@rel="next"]/@href').extract()
    	if next_links:
    		yield Request(
                            response.urljoin(next_links[0]), 
                            self.parse_category, 
                            meta={'category':response.meta['category']}
                            )

    #######################################################################
    # parse category string and returns type character.
    def get_type_by_category(self, category):        
        ret_type = u'R' if "ACCESSORIES" in category else u'A'
        if "SHOES" in category: ret_type = u'S'
        if "BAGS" in category: ret_type = u'B'
        if "JEWELLERY" in category: ret_type = u'J'
        return ret_type

    #######################################################################
    # Callback to process product page
    def parse_item(self, response):
        prices = response.xpath('//p[@itemprop="offers"]//text()').re('[\d.,]+')        
        currency = re.findall(r'config.currentCurrency\s*=\s*\"(\w+)\"', response.body)
        specs = response.xpath('//*[@class="option-size"]/ul/li')

    	item = CoastdemoItem()
    	item['code']           = response.url.split('/')[-1]
    	item['name']           = response.xpath('//meta[@itemprop="name"]/@content').extract_first().title()
    	item['description']    = response.xpath('//meta[@itemprop="description"]/@content').extract_first()
    	item['designer']       = u'Coast' # if the info exists replace query with default string.
    	item['raw_color']      = response.xpath('//li[@class="active"]/span/text()').extract_first()
    	item['price']          = "%.2f" % float(prices[0])

    	item['currency']       = currency[0] if currency else "GBP"
    	item['sale_discount']  = item['price'] if len(prices) < 2 else "%.2f" % float(prices[1])
    	item['link']           = response.url
        item['type']           = self.get_type_by_category(response.meta['category'].upper())
    	item['gender']         = u"F" # The website has only women's goods.
    	item['stock_status']   = {}
    	for spec in specs:
    		item['stock_status'][spec.xpath('./a/text()').extract_first()] = not(spec.xpath('./@class') == "no-stock")
    	
    	item['skus']           = response.xpath('//meta[@name="keywords"]/@content').extract_first().split(",")    	    	
    	item['image_urls']     = response.xpath('//*[@class="prod-image"]/div/div/img/@src').extract()

    	yield item


