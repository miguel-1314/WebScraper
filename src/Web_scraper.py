import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv
import re
import unidecode

driver = webdriver.Firefox(executable_path='/Users/JRamon/Downloads/geckodriver')

#Driver de selenium 
#driver = webdriver.Firefox(executable_path = '..\geckodriver.exe')
#Pagina web de World Padel Tour en la que nos aparece un listado con todos los jugadores, tanto
#del ranking masculino como del ranking femenino
link_players = 'https://www.worldpadeltour.com/jugadores/'
index = 'https://www.worldpadeltour.com'

#Definimos cabecera distinta a la por defecto
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

#Lista de atributos de jugadores, divididos en 3 arrays distintos por simplicidad, dado que cada uno
#de los arrays aparece en un punto determinado de la página
player_attributes_one = ["name","ranking", "puntos", "partidos_jugados","partidos_ganados","partidos_perdidos","efectividad","racha_victorias"]
player_attributes_two = ["compañero", "posicion", "lugar nacimiento", "fecha nacimiento", "altura", "residencia"]
statistics_attributes = ["partidos jugados", "partidos ganados", "efectividad", "campeon", "finalista", "semifinalista", "cuartos", "octavos", "dieciseisavos"]
years = ["2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013"]

#Función que elimina los acentos de un cadena de caracteres, así como de convertir algunas 
#cadenas en otras que nos interesen
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

#Método que separa la cadena de NombreApellido1Apellido2 en Nombre, Apellido 1 y Apellido 2
# y que convierte a letra minuscula para la posterior construcción de la URL
def camel_case_split(name):
	splitted = re.sub('([A-Z][a-z]+)', r' \1',re.sub('([A-Z]+)', r' \1', name)).split()
	converted_list = [x.lower() for x in splitted]
	return converted_list

#Función que compone la URL específica del recurso jugador con '-' para concordar con el formato de URL que utiliza
#el sitio web
def compose_url(array_name):
	new_url = '-'.join(array_name)
	return remove_accents(new_url)

#Función principal que construye la url final de cada jugador, añadiendo el prefijo de World Padel Tour
#para todos los jugadores
def build_url(name):
	compound_url = link_players + compose_url(camel_case_split(name)) + '/'
	return compound_url

def get_attributes(url_player):
    web_player = requests.get(url_player)
    player_list_one = []
    player_list_two = []
    if(web_player.status_code == 200) :
        content_player = BeautifulSoup(web_player.content, "lxml")
        #Nombre del jugador
        player_list_one.append(content_player.find('h1', class_='c-ranking-header__title').text)
        i = 1
        for data in content_player.find_all('div', class_='c-ranking-header__data-box'):
            new_data = data.find('p', class_='c-ranking-header__data').text
            print(player_attributes_one[i] + " : "  + new_data)
            player_list_one.append(new_data)
            i+=1
        j = 0
        for more_data in content_player.find_all('li', class_='c-player__data-item'):
            item = more_data.find('p').text
            print(player_attributes_two[j] + " : "  + item)
            player_list_two.append(item)
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
    else:
    	print('it doesnt connect')
    return player_list_one + player_list_two

#Procdimiento que persiste a un jugador en un fichero CSV
def persist(player):
	with open('statistics_players.csv', 'a', newline='') as csvfile:
		storer = csv.writer(csvfile, delimiter='|', quotechar='.', quoting=csv.QUOTE_MINIMAL)
		storer.writerow(player)

#Procedimiento que prepara todo lo necesario para el procesamiento de un jugador:
# Llama a las funciones que construyen la url.
# A la que obtiene los atributos que queremos almacenar en el fichero csv.
# A la que almacena la fila del jugador en el csv.
def process_player(name):
	url_player = build_url(name)
	print("Procesando: ", url_player)
	player = get_attributes(url_player)
	print(player)
	if player != []:
		persist(player)

#Procedimiento principal que llama a todas las funciones definidas.
# Realiza un scroll down con Selenium en la página de resumen 
# donde se muestran los jugadores, para principalmente obtener todos los jugadores de Padel.
def scroll_down(driver, link):
	driver.get(link)
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	print("Cargando datos.")
	time.sleep(3)

	web = driver.page_source
	content = BeautifulSoup(web, "lxml")
	count = 1 #Player counter

	for player in content.find_all('li', class_='c-player-card__item'):
		#if count == 10:
			#break

		name = player.find('div', class_='c-player-card__name').text
		score = player.find('div', class_='c-player-card__score').text
		print("Jugador / puntuacion \n")
		print(name + '\n' + score)
		print(" ··········· \n")
		process_player(name)
		time.sleep(10)
		count += 1

	print("Contador de jugadores ", count)
	driver.close()

#-------------------------------------------- main
persist(player_attributes_one + player_attributes_two) #añadimos cabecera al csv
scroll_down(driver, link_players)
