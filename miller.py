import scrapy, logging, csv
import pandas as pd
from scrapy.crawler import CrawlerProcess

csvName = 'Mills-Output.csv' 
tda = ['Title', 'Product-ID', 'Product-SKU', 'Regular-Price', 'Sale-Price', 'Sale', 'Product-URL', 'Images']

def dataframeDiff(dframe):
	df = pd.read_csv(dframe, encoding='cp1252')
	print(df)
	df.to_csv('dataframe.csv')

def writeRow(ary):
	with open(csvName, "a") as w:
		csvWriter = csv.writer(w, delimiter=',')
		csvWriter.writerow(ary)

class millsSpider(scrapy.Spider):
	"""Mills Fleet Farm Price Crawler"""
	name = 'mills-spider'
	outputFolder = 'database'
	start_urls = ['https://www.fleetfarm.com']
	logging.getLogger('scrapy').propagate = False

	def start_requests(self):
		allCategories = ['hunting', 'fishing', 'sports-outdoors', 'tires-automotive',
						'clothing-footwear', 'home', 'food-household', 'pets-wild-bird'
						'lawn-garden', 'farm-livestock', 'home-improvement', 'toys']
		#allCamping = '/category/sports-outdoors/camping/_/N-1453582648?null&Nrpp=99999'
		#url = f'{self.start_urls[0]}{allCamping}'
		#yield scrapy.Request(url=url, callback=self.getCards)
		
		for category in allCategories:
			url = f'{self.start_urls[0]}/category/{category}?null&Nrpp=25'
			yield scrapy.Request(url=url, callback=self.getCards)

	def getCards(self, response):
		tiles = response.xpath('//div[@class="product-tile"]')
		productUrls = tiles.xpath('//div[@class="product-image"]//a/@href').getall()

		for url in productUrls:
			url = url.split(';')[0]
			url = f'{self.start_urls[0]}{url}'
			#url = 'https://www.fleetfarm.com/detail/camelbak-21-oz-white-black-podium-chill-bike-bottle/0000000393330?Ntt=elBak%2021%20oz%20White%20Black%20Podium'#url = 'https://www.fleetfarm.com/detail/reliance-bio-blue-toilet-deodorant-24-pk/0000000389377?bc=10708|10811'#'https://www.fleetfarm.com/detail/mtn-ops-2-oz-energy-shot-pineapple-shot/0000000376969'
			yield scrapy.Request(url=url, callback=self.recursiveParse)

	def recursiveParse(self, response):
		title = response.xpath('//h1[@class="product-name"]/text()').get()
		title = title.strip().replace('w/', '').replace('\t', '').replace('\'', '').replace('\\', '')

		saleOrigPrice = response.xpath('//div[@class="product-price price"]//div[@class="original-price"]//span[@itemprop="price"]/text()').get()
		salePrice = response.xpath('//div[@class="product-price price"]//div[@class="sale-price"]//span[@id="regular-price"]/text()').get()
		regularPrice = response.xpath('//div[@class="product-price price"]//div[@class="regular-price"]//span[@id="regular-price"]/text()').get()
		
		imgs = response.xpath('//img[@class="viewer-thumb-image"]/@src').getall()#//img[@class="viewer-thumb-image"]/@src').get()
		imgs = [f'{self.start_urls[0]}{img}' for img in imgs]

		productID = response.xpath('//div[@class="product-details"]//div[@class="product-number"]//span[@itemprop="productID"]/text()').get()
		productSKU = response.xpath('//div[@class="product-sku "]//span[@class="sku-number"]/text()').get()
		productURL = response.url

		if salePrice != None:
			salePrice = salePrice.replace('\t', '').replace('\n', '')
			salePrice = salePrice.split(f'\xa0SALE')[0]
			row = [title, productID, productSKU, saleOrigPrice, salePrice, True, productURL, imgs]
		
		elif salePrice == None:
			row = [title, productID, productSKU, regularPrice, 'NaN', False, productURL, imgs]

		writeRow(row)
		print(row)
	
	open(csvName, 'w+').close()
	writeRow(tda)

if __name__ == "__main__":
	process = CrawlerProcess()
	process.crawl(millsSpider)
	process.start()
	dataframeDiff(csvName)