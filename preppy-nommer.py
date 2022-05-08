import scrapy, logging, time, json, re, os
import requests, pdfkit, unidecode
from scrapy.crawler import CrawlerProcess

class preppySpider(scrapy.Spider):
	"""Collect food recipes without the abhorrently excessive ads and life stories"""
	name = 'preppy-nommer'
	outputFolder = 'database'
	start_urls = ['https://preppykitchen.com/category/recipes/']
	handle_httpstatus_list = [404]
	logging.getLogger('scrapy').propagate = False # No Excessive Log
	convertPdfPath = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe' # force path for html to pdf bin
	config = pdfkit.configuration(wkhtmltopdf=convertPdfPath)

	def start_requests(self): # Scrape several food category urls
		urlSuffix = ["main-dishes", "desserts", "breakfast", "side-dishes",
					"breads", "soups", "salads", "casseroles","instant-pot",
					"appetizers", "drinks", "holiday"]

		urls = [f'{self.start_urls[0]}{x}' for x in urlSuffix] # List of full URLs, domain + category
		for url in urls: # For each url/category, run pagination function
			yield scrapy.Request(url=url, callback=self.getPagination, cb_kwargs=dict(category=url.split('/')[-1])) # Carry category as function
	
	def getPagination(self, response, category): # Get highest 'page number' from bottom of category url
		pageList = [] # Empty array for parsing highest page number
		for x in response.xpath('//*[@id="genesis-content"]/div[2]/ul/li/a/@href'): # Xpath for 'pagination' footer section
			pageList.append(x.get()) # Append array with url of each listed page
		
		highPage = 0 # Initialize variable as integer
		for page in pageList: 
			indx = page[-2] # Index of page number within url string

			try: # Try to convert index to integer
				num = int(indx)
			except: # Otherwise index is not a number, do nothing
				continue

			if highPage < num: # If current index is greater than previous page integer
				highPage = num # Set as new highest page integer

		for x in range(1, highPage + 1): # Generate urls for every page number up to and including highest page
			fullUrl = f'{response.request.url}/page/{x}'
			yield scrapy.Request(url=fullUrl, callback=self.parse, cb_kwargs=dict(category=category))

	def parse(self, response, category):
		for recip in response.xpath('//header[@class="entry-header"]'):
			urls = recip.xpath('//a[@class="entry-image-link"]//@href').getall()
		print(category)
		try:
			for url in urls:
				yield scrapy.Request(url=url, callback=self.recursiveParse, cb_kwargs=dict(category=category))
			
		except Exception as e: # Redundant and ugly but w/e
			with open('error.txt', 'a') as a:
				print(f'{e}: {response.request.url}')
				a.write(f'{e}: {response.request.url}\n')

	def recursiveParse(self, response, category):
		try:
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

if __name__ == "__main__":
	process = CrawlerProcess()
	process.crawl(preppySpider)
	process.start()