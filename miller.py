import scrapy, logging, time, csv
import pandas as pd
from scrapy.crawler import CrawlerProcess

csvName = 'Mills-Output.csv' 
errName = 'Mills-Error.csv'
tda = ['Title', 'Sub-Category', 'Product-ID', 'Product-SKU', 'Regular-Price', 'Sale-Price', 'Sale', 'Product-URL', 'Category', 'Images']

def dataframeDiff(dframe):
	df = pd.read_csv(dframe, encoding='cp1252')
	print(df)
	df.to_csv('dataframe.csv')

def writeRow(cName, ary):
	with open(cName, "a") as w:
		csvWriter = csv.writer(w, delimiter=',')
		csvWriter.writerow(ary)

class millsSpider(scrapy.Spider):
	"""Mills Fleet Farm Price Crawler"""
	name = 'mills-spider'
	outputFolder = 'database'
	start_urls = ['https://www.fleetfarm.com']
	logging.getLogger('scrapy').propagate = False
	itemsPerPage = 99999
	counter = 0

	def start_requests(self): # Recursively scrape cards from main department categories
		allCategories = ['hunting/_/N-1096313067', 'fishing/_/N-1191395697', 'sports-outdoors/_/N-817546303',
						'tires-automotive/_/N-3033881547', 'clothing-footwear/_/N-3941125009',
						'home/_/N-4001179884', 'food-household/_/N-563764611', 'toys/_/N-3859731678',
						'pets-wild-bird/_/N-2832316490', 'lawn-garden/_/N-3059100830',
						'farm-livestock/_/N-1885444951', 'home-improvement/_/N-3069115488']
		
		for category in allCategories:
			url = f'{self.start_urls[0]}/category/{category}'
			yield scrapy.Request(url=url, callback=self.getSubCategory)

	def getSubCategory(self, response): # Get subcategories. ie: Auto > Tires/Accessories, Clothes > Shoes
		urlAry = []

		if response.url.split('/')[-3] == 'toys':
			url = f'{response.url}?null&Nrpp={self.itemsPerPage}'
			urlAry.append(url)

		else:
			subCategories = response.xpath('//div[@class="section-content"]//ul[@class="promo-grid promo-static-stack-grid-five"]//li[@class="promo-tile "]//@href').getall()
			urls = [f'{self.start_urls[0]}{cat}?null&Nrpp={self.itemsPerPage}' for cat in subCategories]
			[urlAry.append(url) for url in urls]

		for url in urlAry:
			yield scrapy.Request(url=url, callback=self.getCards)

	def getCards(self, response):
		print(f'{response.url}: Loading new subcategory...\n')
		tiles = response.xpath('//div[@class="product-tile"]')
		productUrls = tiles.xpath('//div[@class="product-image"]//a/@href').getall()

		for url in productUrls:
			url = url.split(';')[0]
			url = f'{self.start_urls[0]}{url}'
			yield scrapy.Request(url=url, callback=self.recursiveParse)

	def recursiveParse(self, response):
		title = response.xpath('//h1[@class="product-name"]/text()').get()
		title = title.strip().replace('w/', '').replace('\t', '').replace('\'', '').replace('\\', '')

		categry = response.xpath('//section[@class="breadcrumbs"]//ul[@aria-label="breadcrumbs"]//a/text()').getall()  
		subcat = categry[-1]
		categry = ['/'.join(categry) for i in categry]

		saleOrigPrice = response.xpath('//div[@class="product-price price"]//div[@class="original-price"]//span[@itemprop="price"]/text()').get()
		salePrice = response.xpath('//div[@class="product-price price"]//div[@class="sale-price"]//span[@id="regular-price"]/text()').get()
		regularPrice = response.xpath('//div[@class="product-price price"]//div[@class="regular-price"]//span[@id="regular-price"]/text()').get()
		
		imgs = response.xpath('//img[@class="viewer-thumb-image"]/@src').getall()#//img[@class="viewer-thumb-image"]/@src').get()
		imgs = [f'{self.start_urls[0]}{img}' for img in imgs]

		productID = response.xpath('//div[@class="product-details"]//div[@class="product-number"]//span[@itemprop="productID"]/text()').get()
		productSKU = response.xpath('//div[@class="product-sku "]//span[@class="sku-number"]/text()').get()
		productURL = response.url

		if salePrice != None:
			salePrice = salePrice.replace('\t', '').replace('\n', '').replace('\xa0CLEARANCE', '\xa0SALE')
			salePrice = salePrice.split(f'\xa0SALE')[0]
			row = [title, subcat, productID, productSKU, saleOrigPrice, salePrice, True, productURL, categry, imgs]
		
		elif salePrice == None:
			row = [title, subcat, productID, productSKU, regularPrice, 'NaN', False, productURL, categry, imgs]

		self.counter += 1
		writeRow(csvName, row)
		print(f'\n.:##| {self.counter} |##:.\n{row}')
		#print(f'{self.counter}\n{row}')
		time.sleep(.2)
	
	open(csvName, 'w+').close()
	writeRow(csvName, tda)

if __name__ == "__main__":
	process = CrawlerProcess()
	process.crawl(millsSpider)
	process.start()
	dataframeDiff(csvName)