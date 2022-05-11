import scrapy, shutil, logging, time, json, re, os
import requests, pdfkit, unidecode
from scrapy.crawler import CrawlerProcess
from pprint import pprint

class sallySpider(scrapy.Spider):
	"""Collect food recipes without the abhorrently excessive ads and life stories
	Will crawl any site that is formatted as follows (with minor tweaking).
	Category drop down/url suffixs. Grab all links for every page in pagination footer. Get header, picture and card (to pdf) download."""
	name = 'sally-nommer'
	outputFolder = 'database'
	start_urls = ['https://sallysbakingaddiction.com']
	user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
	logging.getLogger('scrapy').propagate = False # No Excessive Log
	convertPdfPath = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe' # force path for html to pdf bin
	config = pdfkit.configuration(wkhtmltopdf=convertPdfPath)
	x = 0

	def start_requests(self): # Scrape several food category urls
		urlSuffix = ['desserts', 'breakfast-treats', 'desserts/brownies-bars',
					'desserts/cakes', 'desserts/candy', 'desserts/cheesecake',
					'desserts/cookies', 'desserts/cupcakes', 'desserts',
					'savory-recipes/dinner', 'desserts/frostings', 'healthy-recipes',
					'desserts/ice-cream-frozen-treats', 'breakfast-treats/muffins',
					'desserts/pies-crisps-tarts', 'savory-recipes', 'desserts/specialty-dessert']

		urls = [f'{self.start_urls[0]}/category/{x}' for x in urlSuffix] # List of full URLs, domain + category
		for url in urls: # For each url/category, run pagination function
			yield scrapy.Request(url=url, callback=self.getPagination, cb_kwargs=dict(category=url.split('/')[-1])) # Carry category as function
	
	def getPagination(self, response, category): # Get highest 'page number' from bottom of category url
		pageList = [] # Empty array for parsing highest page number
		pageFooterXpath = '//div[@class="page-numbers-container"]/a[@class="page-numbers"]/span/text()'
		for x in response.xpath(pageFooterXpath): # Xpath for 'pagination' footer section
			pageList.append(x.get()) # Append array with url of each listed page

		lastPageForLoop = int(pageList[-1]) + 1
		for x in range(1, lastPageForLoop): # Generate urls for every page number up to and including highest page
			fullUrl = f'{response.request.url}page/{x}'
			yield scrapy.Request(url=fullUrl, callback=self.parse, cb_kwargs=dict(category=category))

	def parse(self, response, category):
		for url in response.xpath('//div[@class="recipe-title"]//@href').getall():
			yield scrapy.Request(url=url, callback=self.recursiveParse, cb_kwargs=dict(category=category))

	def recursiveParse(self, response, category):
		try:
			self.x += 1
			print(f'\n.:##| {self.x} |##:.\n')
			header = unidecode.unidecode(response.xpath('//h1[@class="page-title header-left"]/text()').get())
			header = header.strip()
			img = response.xpath('//div[@class="tasty-recipes-image"]//img/@src').extract()
			img = img[-1].replace('-265x265', '')
			card = response.xpath('//div[@class="print-the-recipe-button"]//a/@href').get()
			card = f'{response.request.url}{card}'
			recipeID = card.split('/')[-1]
			
			jLog = {'name' : header,
					'image' : img,
					'id' : recipeID,
					'category' : category,
					'card' : card}
			
			header = header.replace(" ", "-").replace("'", "").replace('!', '').replace('(R)', '').replace('(', '').replace(')', '') # Format header into lowercase, dash seperated for file naming
			filename = header.replace('&', '').replace('+', '').replace(',', '').replace(':', '').replace('---', '').replace('--', '-')
			filename = filename.lower()
			nestedFolder = f'.\\{self.outputFolder}\\{filename}\\' # Nest a folder named 'Recipe' within folder name of 'Category'
			
			if not os.path.exists(nestedFolder): # If \Category\Recipe folder doesn't exist...
				os.makedirs(nestedFolder) # make it
				with open(f'{nestedFolder}{filename}.txt', 'w') as j: # Create json log file of scraped info
					json.dump(jLog, j)	
				pdfkit.from_url(card, f'{nestedFolder}{filename}.pdf', configuration=self.config)

				headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
				response = requests.get(img, headers=headers, stream=True)
				if response.status_code == 200:
					with open(f'{nestedFolder}{filename}.jpg', 'wb') as wb:
						shutil.copyfileobj(response.raw, wb)
						print(f'{nestedFolder}{filename}')
						print(response.status_code, category)
					del response
				pprint(img)

		except Exception as e:
				with open('error.txt', 'a') as a:
					print(f'{e}: {response.request.url}')
					a.write(f'{e}: {response.request.url}\n')

if __name__ == "__main__":
	process = CrawlerProcess()
	process.crawl(sallySpider)
	process.start()

#2.64hrs - JSON/PDF/JPG