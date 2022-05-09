import scrapy, shutil, logging, time, json, re, os
import requests, pdfkit, unidecode
from scrapy.crawler import CrawlerProcess
from pprint import pprint

class mffSpider(scrapy.Spider):
	"""Mills Fleet Farm Price Crawler"""
	name = 'fleet-farm-spider'
	outputFolder = 'database'
	start_urls = ['https://www.fleetfarm.com']
	logging.getLogger('scrapy').propagate = False

	def start_requests(self):
		allCamping = '/category/sports-outdoors/camping/_/N-1453582648?null&Nrpp=20'
		url = f'{self.start_urls[0]}{allCamping}'
		yield scrapy.Request(url=url, callback=self.getCards)

	def getCards(self, response):
		tiles = response.xpath('//div[@class="product-tile"]')
		productUrls = tiles.xpath('//div[@class="product-image"]//a/@href').getall()

		for url in productUrls:
			url = url.split(';')[0]
			url = f'{self.start_urls[0]}{url}'
			url = 'https://www.fleetfarm.com/detail/mtn-ops-2-oz-energy-shot-pineapple-shot/0000000376969'
			yield scrapy.Request(url=url, callback=self.recursiveParse)

	def recursiveParse(self, response):
		title = response.xpath('//h1[@class="product-name"]/text()').get()
		title = title.strip().replace('w/', '').replace('\t', '').replace('\'', '').replace('\\', '')

		price = response.xpath('//span[@itemprop="price"]//text()').get()
		#print(price)

		salePrice = response.xpath('//div[@class="sale-price"]//span[@id="regular-price"]//text()').get()
		salePrice = salePrice.strip().replace('\t', '').replace('\n', '').replace(' ', '')
		print(salePrice)
		#price = response.xpath('//div[@class="regular-price"]//span/text()').get()
		img = response.xpath('//img[@class="viewer-main-image"]//@src').get()


		#print(f'{self.start_urls[0]}{img}')
		#for url in productUrls:
		#	print(f'{self.start_urls[0]}{url}\n\n')
		#class=
		#print(ul)
		#for li in ul:
		#	print(li)#.xpath('//div["class="product-tile"]'))

if __name__ == "__main__":
	process = CrawlerProcess()
	process.crawl(mffSpider)
	process.start()