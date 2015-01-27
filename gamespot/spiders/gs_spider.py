import scrapy
from gamespot.items import *
import urllib2, json
import numpy as np


class gsLinkSpider(scrapy.Spider):
	name = 'gsLink'
	allowed_domains = ['gamespot.com']
	start_urls = ['http://www.gamespot.com/reviews/?page=%d' % x for x in range(1, 32)]

	def parse(self, response):
		for sel in response.xpath('//article[@class="media media-review"]'):
			link = gsLink()
			link['reviewLink'] = sel.xpath('a/@href').extract()[0]
			yield link

class gsSpider(scrapy.Spider):
	name = 'gs'
	allowed_domains = ['gamespot.com']
	start_urls = np.unique(['http://gamespot.com'+x['reviewLink'] for x in json.load(open('json/gamespotLinks.json'))])
	#start_urls = ['http://www.ign.com/games/1942-joint-strike/ps3-14240367']
	
	def parse(self, response):
		game = gsItem()
		game['name'] = response.xpath('//span[@itemprop="itemreviewed"]/text()').extract()[0]
		game['review'] = ' '.join(response.xpath('//section[@class="article-body typography-format "]/p/text()').extract())
		game['gsScore'] = response.xpath('//div[@class="gs-score__cell"]/span/span/text()').extract()[0]
		game['commScore'] = response.xpath('//dl[@class="breakdown-reviewScores__userAvg align-vertical--child"]/dt/a/text()').extract()[0]
		game['nRatings'] = response.xpath('//dl[@class="breakdown-reviewScores__userAvg align-vertical--child"]/dd/text()').extract()[0].split()[0]
		game['genre'] = response.xpath('//dl[@class="pod-objectStats-additional"]/dd')[2].xpath('a/text()').extract()

		contributors = []
		for c in response.xpath('//article[@class="fyre-comment-article"]'):
			contributors.append(c.xpath('div/header/a/text()').extract()[0])
		game['contributors'] = contributors


		#game['platforms'] = response.xpath('//div[@class="contentPlatformsText"]/span/a/text()').extract()
		#try:
		#	if len(response.xpath('//a[@class="scoreBox-scoreLink"]/span/text()')) > 0:
		#		game['ignScore'] = float(response.xpath('//a[@class="scoreBox-scoreLink"]/span/text()').extract()[0])
		#	else:
		#		game['ignScore'] = float(response.xpath('//div[@class="ignRating ratingRow"]/div[@class="ratingValue"]/text()').extract()[0])
		#except:
		#	pass
		#game['reviewLink'] = response.xpath('//a[@title="review"]/@href').extract()[0]
		#try: game['releaseDate'] = ' '.join(response.xpath('//div[@class="gameInfo-list leftColumn"]/div/text()').extract()[1].split())[1:]
		#except: pass
		#for d in response.xpath('//div[@class="gameInfo-list"]/div'):
		#	title = d.xpath('strong/text()').extract()[0]
		#	if title == 'Genre': game['genre'] = ' '.join(d.xpath('a/text()').extract()[0].split())
		#	elif title == 'Publisher': game['publisher'] = ' '.join(d.xpath('a/text()').extract()[0].split())
		#	elif title == 'Developer': game['developer'] = ' '.join(d.xpath('a/text()').extract()[0].split())
		#	elif title == 'Release Date': game['releaseDate'] = ' '.join(d.xpath('text()').extract()[0].split())[1:]
		#commScore = response.xpath('//div[@class="communityRating ratingRow"]')
		#if len(commScore) > 0:
		#	try:
		#		game['commScore'] = float(commScore[0].xpath('div[@class="ratingValue"]/text()').extract()[0])
		#		game['nRatings'] = int(commScore[0].xpath('div[@class="ratingCount"]/b/text()').extract()[0])
		#	except:
		#		pass
		yield game



			
