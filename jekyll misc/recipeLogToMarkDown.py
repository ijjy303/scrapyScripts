import json, os

dr = r''

for root, dirs, files in os.walk(dr):
	for jLog in files:
		if jLog.endswith('.txt') and jLog != 'error.txt':
			with open(f'{root}\\{jLog}', 'r') as r:
				jj = json.load(r)

				title = jj['name']
				category = jj['category'].replace('-', ' ').title()
				catDash = category.replace(' ', '-').lower()
				filename = jj['name'].replace(' ', '-').lower()

				with open(f'.\\mds\\{filename}.md', 'w+') as w:
					w.write('''---
title: "%s"
image:
    path: /images/recipes/%s/%s/%s.jpg
    thumbnail: /images/recipes/%s/%s/%s.jpg
tags:
- Recipe
- %s
---
<center><a href="/example/images/recipes/%s/%s/%s.pdf">Recipe PDF</a></center>
''' % (title, catDash, filename, filename, catDash, filename, filename, category, catDash, filename, filename))