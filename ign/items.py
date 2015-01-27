# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ignLink(scrapy.Item):
    pageLink = scrapy.Field()
    reviewLink = scrapy.Field()
    boxart = scrapy.Field()

class ignItem(scrapy.Item):
    name = scrapy.Field()
    platforms = scrapy.Field()
    reviewDate = scrapy.Field()
    releaseDate = scrapy.Field()
    ignScore = scrapy.Field()
    commScore = scrapy.Field()
    nRatings = scrapy.Field()
    reviewLink = scrapy.Field()
    publisher = scrapy.Field()
    developer = scrapy.Field()
    genre = scrapy.Field()

class ignReview(scrapy.Item):
	reviewText = scrapy.Field()
	reviewURL = scrapy.Field()
