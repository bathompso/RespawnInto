import scrapy
from ign.items import *
import urllib2, json
import numpy as np


class ignLinkSpider(scrapy.Spider):
	name = 'ignLink'
	allowed_domains = ['ign.com']
	start_urls = ['http://www.ign.com/games/reviews?startIndex=%d' % x for x in range(0, 10000, 25)]

	def parse(self, response):
		for sel in response.xpath('//div[@class="clear itemList-item"]'):
			link = ignLink()
			link['reviewLink'] = sel.xpath('div/ul/li/a/@href').extract()[0]
			link['pageLink'] = sel.xpath('div/div[@class="item-title"]/h3/a/@href').extract()[0]
			link['boxart'] = sel.xpath('div/a/img[@class="item-boxArt"]/@src').extract()[0]
			yield link

class ignSpider(scrapy.Spider):
	name = 'ign'
	allowed_domains = ['ign.com']
	start_urls = np.unique(['http://ign.com'+x['pageLink'] for x in json.load(open('json/ignLinks.json'))])
	#start_urls = ['http://www.ign.com/games/1942-joint-strike/ps3-14240367']
	
	def parse(self, response):
		game = ignItem()
		game['name'] = ' '.join(response.xpath('//h1[@class="contentTitle"]/a/text()').extract()[0].split())
		try: game['reviewDate'] = response.xpath('//div[@class="releaseDate"]/strong/text()').extract()[0]
		except: pass
		game['platforms'] = response.xpath('//div[@class="contentPlatformsText"]/span/a/text()').extract()
		try:
			if len(response.xpath('//a[@class="scoreBox-scoreLink"]/span/text()')) > 0:
				game['ignScore'] = float(response.xpath('//a[@class="scoreBox-scoreLink"]/span/text()').extract()[0])
			else:
				game['ignScore'] = float(response.xpath('//div[@class="ignRating ratingRow"]/div[@class="ratingValue"]/text()').extract()[0])
		except:
			pass
		game['reviewLink'] = response.xpath('//a[@title="review"]/@href').extract()[0]
		try: game['releaseDate'] = ' '.join(response.xpath('//div[@class="gameInfo-list leftColumn"]/div/text()').extract()[1].split())[1:]
		except: pass
		for d in response.xpath('//div[@class="gameInfo-list"]/div'):
			title = d.xpath('strong/text()').extract()[0]
			if title == 'Genre': game['genre'] = ' '.join(d.xpath('a/text()').extract()[0].split())
			elif title == 'Publisher': game['publisher'] = ' '.join(d.xpath('a/text()').extract()[0].split())
			elif title == 'Developer': game['developer'] = ' '.join(d.xpath('a/text()').extract()[0].split())
			elif title == 'Release Date': game['releaseDate'] = ' '.join(d.xpath('text()').extract()[0].split())[1:]
		commScore = response.xpath('//div[@class="communityRating ratingRow"]')
		if len(commScore) > 0:
			try:
				game['commScore'] = float(commScore[0].xpath('div[@class="ratingValue"]/text()').extract()[0])
				game['nRatings'] = int(commScore[0].xpath('div[@class="ratingCount"]/b/text()').extract()[0])
			except:
				pass
		yield game


class ignReviewSpider(scrapy.Spider):
	name = 'ignReviews'
	allowed_domains = ['ign.com']
	start_urls = [x['reviewLink'] for x in json.load(open('json/ignLinks.json'))]
	
	def parse(self, response):
		review = ignReview()
		review['reviewText'] = ' '.join(response.xpath('//div[@id="article-content"]/p/text()').extract())
		review['reviewURL'] = [x.split('"')[1].replace('\/','/') for x in response.xpath('//div[@class="commentFrame"]').extract().splitlines() if x.find('disqus_url') > 0][0]
		yield review


			
