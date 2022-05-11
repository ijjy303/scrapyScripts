import json, os

dr = r''

for root, dirs, files in os.walk(dr):
	for jLog in files:
		if jLog.endswith('.txt') and jLog != 'error.txt':
			with open(f'{root}\\{jLog}', 'r') as r:
				j = json.load(r)

				capital_food_title = j['name']
				category_titled = j['category'].replace('-', ' ').title()
				category_filename_dashed = j['category']
				filename_dashed = j['name'].replace(' ', '-').lower()

				with open(f'.\\output\\{category_filename_dashed}.md', 'a') as a:
					a.write(f'''
## <center>{capital_food_title}</center>
<a href="/images/recipes/{category_filename_dashed}/{filename_dashed}/{filename_dashed}.pdf"><img src="/images/recipes/{category_filename_dashed}/{filename_dashed}/{filename_dashed}.jpg" class="center"></a>''')
				print(filename_dashed)