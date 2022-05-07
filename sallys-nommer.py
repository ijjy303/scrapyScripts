import scrapy, logging, time, json, re, os
import requests, pdfkit, unidecode
from scrapy.crawler import CrawlerProcess

class nommerSpider(scrapy.Spider):
	"""Collect food recipes without the abhorrently excessive ads and life stories"""
	name = 'nommer'
	outputFolder = 'database'
	start_urls = ['https://sallysbakingaddiction.com/category/']
	handle_httpstatus_list = [404]
	logging.getLogger('scrapy').propagate = False # No Excessive Log
	#convertPdfPath = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe' # force path for html to pdf bin
	#config = pdfkit.configuration(wkhtmltopdf=convertPdfPath)

	def start_requests(self): # Scrape several food category urls
		urlSuffix = ['desserts']
		""", 'breakfast-treats', 'desserts/brownies-bars',
					'desserts/cakes', 'desserts/candy', 'desserts/cheesecake',
					'desserts/cookies', 'desserts/cupcakes', 'desserts',
					'savory-recipes/dinner', 'desserts/frostings', 'healthy-recipes',
					'desserts/ice-cream-frozen-treats', 'breakfast-treats/muffins',
					'desserts/pies-crisps-tarts', 'savory-recipes', 'desserts/specialty-dessert']"""

		urls = [f'{self.start_urls[0]}{x}' for x in urlSuffix] # List of full URLs, domain + category
		for url in urls: # For each url/category, run pagination function
			yield scrapy.Request(url=url, callback=self.getPagination, cb_kwargs=dict(category=url.split('/')[-1])) # Carry category as function
	
	def getPagination(self, response, category): # Get highest 'page number' from bottom of category url
		pageList = [] # Empty array for parsing highest page number
		pageFooterXpath = '//div[@class="page-numbers-container"]/a[@class="page-numbers"]/span/text()'
		for x in response.xpath(pageFooterXpath):#//*[@id="primary"]/div[4]/div/nav/div/div'): # //*[@id="primary"]/div[4]/div/nav/div/div[2]/a[5] # Xpath for 'pagination' footer section
			pageList.append(x.get()) # Append array with url of each listed page

		lastPageForLoop = 61#int(pageList[-1]) + 1
		#for x in range(1, lastPageForLoop): # Generate urls for every page number up to and including highest page
		#	fullUrl = f'{response.request.url}page/{x}'
			#yield scrapy.Request(url=fullUrl, callback=self.parse, cb_kwargs=dict(category=category))
		fullUrl = f'{response.request.url}page/61'
		yield scrapy.Request(url=fullUrl, callback=self.parse, cb_kwargs=dict(category=category))

	def parse(self, response, category):
		for url in response.xpath('//div[@class="recipe-title"]//@href').getall():
			try:
				yield scrapy.Request(url=url, callback=self.recursiveParse, cb_kwargs=dict(category=category))

			except Exception as e: # Redundant and ugly but w/e
				with open('error.txt', 'a') as a:
					print(f'{e}: {response.request.url}')
					a.write(f'{e}: {response.request.url}\n')

	def recursiveParse(self, response, category):
		try:
			header = unidecode.unidecode(response.xpath('//h1[@class="page-title header-left"]/text()').get())
			header = header.strip()

			print(header)
			img = response.xpath('//div[@class="tasty-recipes-image"]//img/@src').extract()
			bigImg = img[-1].replace('265x265', '500x500')
			print(bigImg)

		except:
			print('error')
			"""
			header = unidecode.unidecode(response.xpath('//h1[@class="entry-title"]/text()').get()) # Some recipes have accented characters, gross.
			img = response.xpath('//div[@class="featured-image-class"]//noscript').get() # Direct img src returns embedded URI
			imgUrl = re.findall(r'src="(.+?)"', img)[0] # Using regex on 'noscript' element to pull link within matched src="" regex
			recipeID = response.xpath('//div[@class="entry-content"]//a/@data-recipe').get()
			recipeUrl = f'https://preppykitchen.com/wprm_print/recipe/{recipeID}' # All recipe print cards are on same subdomain
		
			jLog = {'name' : header,
					'image' : imgUrl,
					'id' : recipeID,
					'category' : category,
					'card' : recipeUrl}

			filename = header.replace(" ", "-").lower() # Format header into lowercase, dash seperated for file naming
			nestedFolder = f'.\\{self.outputFolder}\\{category}\\{filename}\\' # Nest a folder named 'Recipe' within folder name of 'Category'
			
			if not os.path.exists(nestedFolder): # If \Category\Recipe folder doesn't exist...
				os.makedirs(nestedFolder) # make it
				with open(f'{nestedFolder}{filename}.txt', 'w') as j: # Create json log file of scraped info
					json.dump(jLog, j)

				rawImg = requests.get(imgUrl).content # Dirty get/dl img jpg without using builtin scrapy pipelines...
				with open(f'{nestedFolder}{filename}.jpg', 'wb') as i: 
					i.write(rawImg) # ..this nix's excessive scrapy files and reqs only one scipt
				#Especially since using htmltopdf to avoid [intentionally] atrocious html code inside main recipe table 
				pdfkit.from_url(recipeUrl, f'{nestedFolder}{filename}.pdf', configuration=self.config)
		
		except Exception as e: # Redundant and ugly but w/e
			with open('error.txt', 'a') as a:
				print(f'{e}: {response.request.url}')
				a.write(f'{e}: {response.request.url}\n')
"""
if __name__ == "__main__":
	process = CrawlerProcess()
	process.crawl(nommerSpider)
	process.start()