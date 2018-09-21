# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Rule, Request, SitemapSpider
from scrapy.linkextractors import LinkExtractor
from pyquery import PyQuery as PQ
import re

from coastdemo.items import CoastdemoItem

#######################################################################
#                                                                     #
#        CoastSpider Class  (base on SitemapSpider)                   #
#                                                                     #
#######################################################################

class CoastSpider(SitemapSpider):
    name = 'coast_sitemap'
    allowed_domains = ['www.coast-stores.com']
    sitemap_urls  = [
    				'https://coast.btxmedia.com/pws/client/sitemap/PWS/ProductDetailPagesX_0.xml',
    ]

    sitemap_rules = [
        ('/p/','parse_item'),
    ]

    #####################################################################
    # Return:   'A' for apparel
    #           'S' for shoes
    #           'B' for bags
    #           'J' for jewelry
    #           'R' for accessories
    # parse bread-crumbs string and returns type character.
    def get_type_by_crumbs(self, crumbs):        
        ret_type = u'R' if "ACCESSORIES" in crumbs else u'A'
        if "SHOES" in crumbs: ret_type = u'S'
        if "BAGS" in crumbs: ret_type = u'B'
        if "JEWELLERY" in crumbs: ret_type = u'J'
        return ret_type

    #####################################################################
    # Callback to parse product page
    def parse_item(self, response):
        # Read DOM.
        doc = PQ(response.body) 

        # Price info in list variable. There is 2 kinds of price - standard and sales.
        prices    = re.findall('[\d.,]+', doc('p[itemprop="offers"]').text())

        # Currency info - extracted from the raw html text because it is not in the dom tree.
        currency  = re.findall(r'config.currentCurrency\s*=\s*\"(\w+)\"', response.body)

        # Breadcrumb to know what category the product belongs to.
        crumbs    = PQ(doc('.breadcrumbs__desc.text-link')).text().upper()

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
        item['type']            = self.get_type_by_crumbs(crumbs)
        item['gender']          = u"F" # The website has only women's goods.
        
        item['stock_status']    = {}        
        for opt in options:            
            item['stock_status'][opt.text] = not(PQ(opt).parents('li').attr('class') == "no-stock")

        item['skus']            = PQ(doc('meta[name="keywords"]')).attr('content').split(",")
        item['image_urls']      = [PQ(img).attr('src') for img in doc('.prod-image > div img')]
        
        yield item