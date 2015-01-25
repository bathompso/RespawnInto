# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class gsLink(scrapy.Item):
    reviewLink = scrapy.Field()

class gsItem(scrapy.Item):
    name = scrapy.Field()
    platforms = scrapy.Field()
    gsScore = scrapy.Field()
    commScore = scrapy.Field()
    nRatings = scrapy.Field()
    genre = scrapy.Field()
    review = scrapy.Field()
    contributors = scrapy.Field()
