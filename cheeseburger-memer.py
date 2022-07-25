import scrapy, logging, datetime, os, re
from scrapy.crawler import CrawlerProcess

class burgerSpider(scrapy.Spider):
	"""Collect all meme dumps from icanhas.cheezburger.com categories.
	Output to HTML without ads, comments, users, etc..."""

	name = 'burger'
	start_urls = ['https://cheezcake.cheezburger.com/', 'https://memebase.cheezburger.com/cringe', 'https://failblog.cheezburger.com/failbook']
	outputHtml = 'CHEESEBURGER.md'
	logging.getLogger('scrapy').propagate = False # No crazy scrapy log output
	numb = 0 # Counter for successful crawls cuz links are parsed in random pattern.
	nowwie = datetime.datetime.now().strftime("%m/%d/%Y-%H:%M:%S")
	hdr = f'# We Haz Da Meatz<br>\nLast updated: {nowwie}\n<br>\n'
	
	try:
		os.remove(outputHtml)
	except:
		pass
	finally:
		with open(outputHtml, 'a+') as w: 
			w.write(hdr)

	def parse(self, response): # Get all front page article links for any category in start urls
		for url in response.xpath('//div[@class="mu-post-title mu-section mu-inset"]//h1/a/@href').getall(): #('//li[@class="listingThumb"]//a/@href').getall():ild
			yield scrapy.Request(url, callback=self.recursiveParse) # Run meme crawler on correct link

	def recursiveParse(self, response):
		header = response.xpath('//h1[@class="mu-title"]/text()').get() # Title header of article and to be used for collection
		header = re.sub(r"\(.*?\)", "", header) # Remove anything between parens, usually dates
		header = re.sub(r"[^a-zA-Z0-9 ]", "", header) # Remove any special characters
		titles = response.xpath('//span[@class="mu-secondary-bg"]/text()').getall() # Get number [title] for each meme
		imglinks = response.xpath('//div[@class="mu-post "]//div[@class="resp-media-wrap"]//noscript//img[@class="resp-media"]/@src').getall() # Image links
		
		if titles == []: # This article is likely single image of soc med post. Often garbage, uses different xpaths, not worth sorting. Oddball.
			pass
		else:
			self.numb += 1 # Crawling a successful link, up counter.
			nextNumb = self.numb + 1 # If not interested in this meme dump, link to next dump on page
			html = f'## <a href="#linky{nextNumb}" id="linky{self.numb}">{header}</a><br>\n\n'

			for item in zip(titles, imglinks):
				title = item[0]
				link = item[1]
				html += f'<span style="font-size:4em">{title}</span><br><img src="{link}" style="width:100%"><br>\n\n'
		
			html += f'<a href="#linky1">GO TO TOP</a>\n\n'
		
			with open(self.outputHtml, 'a+', encoding='utf-8') as w: 
				w.write(html)
				
if __name__ == "__main__":
	process = CrawlerProcess()
	process.crawl(burgerSpider)
	process.start()