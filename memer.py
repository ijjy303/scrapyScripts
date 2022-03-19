import scrapy, os
from scrapy.crawler import CrawlerProcess

class memerSpider(scrapy.Spider):
	"""Collect all meme dumps from front page of Ebaumsworld.
	Output to HTML without ads, comments, categories, users, etc..."""

	name = 'memer' #allowed_domains = ['www.ebaumsworld.com/']
	start_urls = ['https://www.ebaumsworld.com']
	outputHtml = 'output.html'
	numb = 0 # Counter for successful crawls cuz links are parsed in random pattern.
	
	try:
		os.remove(outputHtml)
	except:
		pass

	def parse(self, response): # Get links for any list item in 'Featured' front page
		for url in response.xpath('//div[@class="featureFeedDetails"]//header/h2/a/@href').getall():
			fullLink = f'{self.start_urls[0]}{url}'
			# Not interested in videos, articles, news... just the memes!
			excludeDomain = ['https://www.ebaumsworld.com/videos', 'https://www.ebaumsworld.com/articles', 'https://gaming.ebaumsworld.com/']
			if any(dmain in fullLink for dmain in excludeDomain):
				pass # Do nothing if not meme dump
			else:
				# Cannot pass enumerated for loop with fullLink cuz meme dumps occur randomly in the wild
				yield scrapy.Request(fullLink, callback=self.recursiveParse) # Run meme crawler on correct link

	def recursiveParse(self, response):
		self.numb += 1 # Crawling a successful link, up counter.
		header = response.xpath('//*[@id="detailPage"]/header/h1/text()').get() # Header for meme collection
		titles = response.xpath('//li[@class="galleryListItem"]//img/@title') # Context/Caption for meme
		links = response.xpath('//li[@class="galleryListItem"]//img/@data-src') # Link to image
		nextNumb = self.numb + 1 # If not interested in this meme dump, link to next dump on page
		html = f'<font size="6"><u><b><a href="#{nextNumb}" id="{self.numb}">{header}</a></u></b></font><br><br><br>\n\n'

		for item in zip(titles, links):
			title = item[0].get()
			link = item[1].get()

			if any(extension in link for extension in ['.jpg', '.jpeg', '.png', '.gif']): # Do not include link if not image (ads, social media, etc...)
				html += f'<font size="4">{title}</font><br><img src="{link}" style="width:100%"><br>\n\n'

		with open(self.outputHtml, 'a+', encoding="utf-8") as w: 
			w.write(html)

if __name__ == "__main__":
	process = CrawlerProcess()
	process.crawl(memerSpider)
	process.start()