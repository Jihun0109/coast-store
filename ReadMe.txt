Implemented in three ways.

1. Standard (by the instruction)
	Filename	: coast.py
	Spidername	: coast
	
	Using of Rules, PyQuery

2. SitemapSpider
	Filename	: coast_sitemap.py
	Spidername	: coast_sitemap
	
	This is easy way to collect almost product links.
        The sitemap xml file is located in "https://coast.btxmedia.com/pws/client/sitemap/PWS/ProductDetailPagesX_0.xml"
	The xml file contains all of product links in the website. Not all homepages have the sitemap file.
	We can check robots.txt file if the sitemap file exists and where it is located.

3. Normal Way
	Filename	: coast_xpath.py
	Spidername	: coast_xpath
	Using Xpath
