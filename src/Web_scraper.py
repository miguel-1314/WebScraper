import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv
import re
import unidecode

#driver = webdriver.Firefox(executable_path='/Users/JRamon/Downloads/geckodriver')

driver = webdriver.Firefox(executable_path = '..\geckodriver.exe')
link_players = 'https://www.worldpadeltour.com/jugadores/'
index = 'https://www.worldpadeltour.com'
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

player_attributes_one = ["ranking", "puntos", "partidos_jugados","partidos_ganados","partidos_perdidos","efectividad","racha_victorias"]
player_attributes_two = ["compañero", "posicion", "lugar nacimiento", "fecha nacimiento", "altura", "residencia"]
statistics_attributes = ["partidos jugados", "partidos ganados", "efectividad", "campeon", "finalista", "semifinalista", "cuartos", "octavos", "dieciseisavos"]
years = ["2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013"]

def remove_accents(raw_text):
    raw_text = re.sub(u"[àáâãäå]", 'a', raw_text)
    raw_text = re.sub(u"[èéêë]", 'e', raw_text)
    raw_text = re.sub(u"[ìíîï]", 'i', raw_text)
    raw_text = re.sub(u"[òóôõö]", 'o', raw_text)
    raw_text = re.sub(u"[ùúûü]", 'u', raw_text)
    raw_text = re.sub(u"[ýÿ]", 'y', raw_text)
    raw_text = re.sub(u"[ª]", 'maria', raw_text)
    raw_text = re.sub(u"[ñ]", 'n', raw_text)
    return raw_text

def camel_case_split(name):
	splitted = re.sub('([A-Z][a-z]+)', r' \1',re.sub('([A-Z]+)', r' \1', name)).split()
	converted_list = [x.lower() for x in splitted]
	return converted_list

def compose_url(array_name):
	new_url = '-'.join(array_name)
	return remove_accents(new_url)

def build_url(name):
	compound_url = link_players + compose_url(camel_case_split(name)) + '/'
	return compound_url

def get_attributes(url_player):
    web_player = requests.get(url_player)
    if(web_player.status_code == 200) :
        content_player = BeautifulSoup(web_player.content, "lxml")
        i = 0
        for data in content_player.find_all('div', class_='c-ranking-header__data-box'):
            new_data = data.find('p', class_='c-ranking-header__data').text
            print(player_attributes_one[i] + " : "  + new_data)
            i+=1
        j = 0
        for more_data in content_player.find_all('li', class_='c-player__data-item'):
            item = more_data.find('p').text
            print(player_attributes_two[j] + " : "  + item)
            j+=1
        statistics_attributes_index = 0
        year_index = 0
        count_statistics = 0
        for statistics in content_player.find_all('span', class_='c-flex-table__item-data'):
            if(count_statistics == 9):
                year_index += 1
                statistics_attributes_index = 0
                count_statistics = 0

            print(years[year_index] + " " + statistics_attributes[statistics_attributes_index] + " : " + statistics.text)
            statistics_attributes_index+=1
            count_statistics+=1
            
  
def process_player(name):
	url_player = build_url(name)
	print("Procesando: ", url_player)
	get_attributes(url_player)

def scroll_down(driver, link):
	driver.get(link)
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	print("Cargando datos.")
	time.sleep(3)

	web = driver.page_source
	content = BeautifulSoup(web, "lxml")
	count = 1 #Player counter

	for player in content.find_all('li', class_='c-player-card__item'):
		name = player.find('div', class_='c-player-card__name').text
		score = player.find('div', class_='c-player-card__score').text
		print("Jugador / puntuacion \n")
		print(name + '\n' + score)
		print(" ··········· \n")
		process_player(name)
		time.sleep(1)
		count += 1

	print("Contador de jugadores ", count)
	driver.close()

#main
scroll_down(driver, link_players)
