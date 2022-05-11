import json, os

dr = r''

for root, dirs, files in os.walk(dr):
	if len(files) < 3:
		print(root.split('\\')[-1], files)