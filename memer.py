import scrapy, datetime, os
from scrapy.crawler import CrawlerProcess
from git import Repo

nowwie = datetime.datetime.now().strftime("%m/%d/%Y-%H:%M:%S")

def fusRoDah():
    try:
        repo = Repo('./')
        repo.git.add(update=True) # Fus ## Add
        repo.index.commit(nowwie) # Roh ## Commit
        origin = repo.remote(name='origin')
        origin.push() # Dah ## Push
    except:
        print('Error') # Fus Roh Duh.
        pass

class baumerSpider(scrapy.Spider):
	"""Collect all meme dumps from front page of Ebaumsworld.
	Output to HTML without ads, comments, categories, users, etc..."""

	name = 'baumer' #allowed_domains = ['www.ebaumsworld.com/']
	start_urls = ['https://www.ebaumsworld.com'] #['https://www.ebaumsworld.com/pictures/?page=1']
	outputHtml = 'README.md'#'output.html'
	numb = 0 # Counter for successful crawls cuz links are parsed in random pattern.
	hdr = f'# All ur Memes R belog to Uz<br>\nLast updated: {nowwie}\n<br>\n'
	
	try:
		os.remove(outputHtml)
		with open(outputHtml, 'a+') as w: 
			w.write(hdr)
	finally:
		pass

	def parse(self, response): # Get links for any list item in 'Featured' front page
		for url in response.xpath('//div[@class="featureFeedDetails"]//header/h2/a/@href').getall(): #('//li[@class="listingThumb"]//a/@href').getall():
			fullLink = f'{self.start_urls[0]}{url}' #'https://www.ebaumsworld.com{url}' # fullLink = f'{self.start_urls[0]}{url}'
			# Not interested in videos, articles, news... just the memes!
			excludeDomain = ['https://www.ebaumsworld.com/videos', 'https://www.ebaumsworld.com/articles', 'https://gaming.ebaumsworld.com/']
			if any(dmain in fullLink for dmain in excludeDomain):
				pass # Do nothing if not meme dump
			else: # Cannot pass enumerated for loop with fullLink cuz meme dumps occur randomly in the wild
				yield scrapy.Request(fullLink, callback=self.recursiveParse) # Run meme crawler on correct link

	def recursiveParse(self, response):
		self.numb += 1 # Crawling a successful link, up counter.
		header = response.xpath('//*[@id="detailPage"]/header/h1/text()').get() # Header for meme collection
		titles = response.xpath('//div[@class="overlay gridOverlay"]/h2/text()')# Context/Caption for meme
		links = response.xpath('//li[@class="galleryListItem"]//img/@data-src') # Link to image
		nextNumb = self.numb + 1 # If not interested in this meme dump, link to next dump on page
		html = f'## <a href="#linky{nextNumb}" id="linky{self.numb}">{header}</a><br>\n\n'

		for item in zip(titles, links):
			title = item[0].get().replace('"', '').replace("'", '').replace('\t', '')
			link = item[1].get()

			if any(extension in link for extension in ['.jpg', '.jpeg', '.png', '.gif']): # Do not include link if not image (ads, social media, etc...)
				html += f'<span style="font-size:4em">{title}</span><br><img src="{link}" style="width:100%"><br>\n\n'
		
		html += f'<a href="#linky1">GO TO TOP</a>\n\n'
		with open(self.outputHtml, 'a+', encoding='utf-8') as w: 
			w.write(html)

if __name__ == "__main__":
	process = CrawlerProcess()
	process.crawl(baumerSpider)
	process.start()
	fusRoDah()