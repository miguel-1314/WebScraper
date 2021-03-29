import requests
from bs4 import BeautifulSoup
import time
import csv

link = 'https://www.worldpadeltour.com/jugadores/?ranking=todos'
headers = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\
*/*;q=0.8",
"Accept-Encoding": "gzip, deflate, sdch, br",
"Accept-Language": "en-US,en;q=0.8",
"Cache-Control": "no-cache",
"dnt": "1",
"Pragma": "no-cache",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/5\
37.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
}

try:
	web = requests.get(link, headers=headers)
except requests.exceptions.RequestException:
	pass

if web.status_code == 200:
	content = BeautifulSoup(web.content, "lxml")

	for player in content.find_all('li', class_='c-player-card__item'):
		print("Jugador / puntuacion \n")
		print(player.find('div', class_='c-player-card__name').string+'\n'+player.find('div', class_='c-player-card__score').string)
		print(" ··········· \n")
else:
	print("Web is not available")
