# RedRip.py, a subreddit image fetcher
# Copyright Mackan <thormax5@gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import argparse
import sys
import requests
import re
from imgurpython import ImgurClient
import configparser
import shutil
import os
from imgurpython.helpers.error import ImgurClientError

Config = configparser.ConfigParser()
Config.read("Config.ini")

def getConfig(section):
	opts = {}
	options = Config.options(section)
	for option in options:
		try:
			opts[option] = Config.get(section, option)
		except:
			opts[option] = None
	return opts

client_id = getConfig("Imgur")["client_id"]
client_secret = getConfig("Imgur")["client_secret"]

client = ImgurClient(client_id, client_secret)

parser = argparse.ArgumentParser(description='Fetches images from subreddits')

requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-r', '--reddit', help='the subreddit to crawl', required=True)

parser.add_argument('-a', '--amount', nargs='?', type=int, help='The amount of submissions to crawl')

def main():
	if not len(sys.argv) > 1:
		parser.print_help()
	else:
		args = parser.parse_args()

		reddit = ""
		red = re.findall(r"/r/([^\s/]+)", args.reddit)
		if len(red) > 0:
			if red[0] is not None:
				reddit = red[0].replace("/r/", "")
		else:
			reddit = args.reddit

		amount = 50;
		if args.amount is not None:
			amount = args.amount

		print("Crawling {} submissions from {}".format(amount, reddit))

		r = requests.get("https://www.reddit.com/r/{}.json?limit={}".format(reddit, amount))
		if r.status_code == 200:
			for post in r.json()["data"]["children"]:
				if post["data"]["domain"].lower() != "self.{}".format(reddit).lower():
					url = post["data"]["url"]
					if url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webm')):
						q = requests.get(url, stream=True)
						if q.status_code == 200:
							if not os.path.exists(reddit):
								os.makedirs(reddit)

							with open("{}/{}".format(reddit, url.rsplit('/', 1)[-1]), 'wb') as f:
								q.raw.decode_content = True
								shutil.copyfileobj(q.raw, f)
					else:
						pattern = r'https?:\/\/(m\.)?imgur\.com\/a\/.*$'
						prog = re.compile(pattern)
						m = prog.search(url.lower())

						if m is not None:
							album = m.group(0).rsplit('/', 1)[-1]
							try:
								images = client.get_album_images(album)
								for image in images:
									q = requests.get(image.link, stream=True)
									if q.status_code == 200:
										if not os.path.exists(reddit):
											os.makedirs(reddit)

										if not os.path.exists("{}/{}".format(reddit, album)):
											os.makedirs("{}/{}".format(reddit, album))

										with open("{}/{}/{}".format(reddit, album, image.link.rsplit('/', 1)[-1]), 'wb') as f:
											q.raw.decode_content = True
											shutil.copyfileobj(q.raw, f)
							except ImgurClientError as e:
								print(e.error_message)
						else:

							pattern = r'https?://(giant\.)?gfycat.com/.*$'
							prog = re.compile(pattern)
							m = prog.search(url)

							if m is not None:
								im = m.group(0).rsplit('/', 1)[-1]
								q = requests.get("http://giant.gfycat.com/{}.webm".format(im), stream=True)
								if q.status_code == 200:
									if not os.path.exists(reddit):
										os.makedirs(reddit)

									with open("{}/{}.webm".format(reddit, im), 'wb') as f:
										q.raw.decode_content = True
										shutil.copyfileobj(q.raw, f)
							else:
								image = url.rsplit('/', 1)[-1]
								if image is not None:
									try:
										img = client.get_image(image)

										if img.link.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webm')):
											q = requests.get(img.link, stream=True)
											if q.status_code == 200:
												if not os.path.exists(reddit):
													os.makedirs(reddit)

												with open("{}/{}".format(reddit, img.link.rsplit('/', 1)[-1]), 'wb') as f:
													q.raw.decode_content = True
													shutil.copyfileobj(q.raw, f)

									except ImgurClientError as e:
										print(e.error_message)


		elif r.status_code == 404:
			print("Couldn't find subreddit {}".format(reddit))
		elif r.status_code == 429:
			print("Couldn't fetch reddit data. Please try again later.")
		else:
			print("Got status code {}".format(r.status_code))


if __name__ == "__main__":
	main()