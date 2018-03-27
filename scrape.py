import urllib.request
from urllib.request import Request, urlopen
import re
from bs4 import BeautifulSoup
import json
import requests, bs4

from flask import Flask

app = Flask(__name__)


def find(source, first, last):
    try:
        start = source.index(first) + len(first)
        end = source.index(last, start)
        return source[start:end]
    except ValueError:
        return ""

@app.route('/')
def index():
    return """
        Car information api containing following endpoints:
        /single_police/regnr/
        /normal/regnr/
        /car/regnr/
    """

@app.route('/car/<regnr>', methods=['GET'])
def car_information(regnr):        
    r = requests.get('https://www.vegvesen.no/kjoretoy/kjop+og+salg/kj%C3%B8ret%C3%B8yopplysninger?registreringsnummer='+regnr.upper())
    soup = bs4.BeautifulSoup(r.text, 'lxml')
    contents = soup.find(class_='text')
    car_object = {}
    for table in contents.find_all(class_='definisjonsliste'):
        titles = table.find_all("dt")
        data = table.find_all("dd")
        for item in range(len(data)):
            car_object[titles[item].text.strip().replace(" ", "_").lower()] = data[item].text.strip()
    
    response = json.dumps(car_object, indent=4, ensure_ascii=False)
    return response
    
    # return json.dumps(car_object, indent=4, ensure_ascii=False)


# @app.route('/all_police/')
# def scrapeAllSivil():
#     req = Request('https://regnr.info/sivilpoliti', headers={'User-Agent': 'Mozilla/5.0'})
#     webpage = urlopen(req).read()
#     soup = BeautifulSoup(webpage, 'html.parser')
#     cars = soup.find_all("div", class_="bilboks-container")

#     car_soup = BeautifulSoup(str(cars), 'html.parser')

#     alle_registreringsnummer = car_soup.find_all("b")
#     alle_merker = car_soup.find_all("div", class_="bilboks-merkemodell")
#     alle_bilder = car_soup.find_all("div", class_="bilboks-bilde")

#     alle_biler = []
#     for i in range(len(alle_registreringsnummer)):
#         regnr = alle_registreringsnummer[i].string
#         merke_model = alle_merker[i].string.strip()
#         bilde = str(alle_bilder[i])[37:-9]
#         data = {'regnr':regnr, 'merke_model':merke_model, 'bilde':bilde}
#         alle_biler.append(data)

#     return json.dumps(alle_biler, indent=4)


@app.route('/single_police/<regnr>')
def scrapeSingleSivil(regnr):
    req = Request('https://regnr.info/' + regnr, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')

    kjoretoy_info = str(soup.find_all("div", class_="kjoretoy-data"))
    kategori = find(kjoretoy_info, "<b>", "</b><br/>").strip()
    type_bil = find(kjoretoy_info, "<h1>","</h1>").strip()
    tilhorer = find(kjoretoy_info, '<a href="/sivilpoliti" style="text-decoration:none;color:red;font-weight:bold;">', "</a>").strip()
    info_politi = find(kjoretoy_info, "</a>\n<br/>", '</span></div>').strip()

    serienummer = find(str(soup.find_all("li")), '<a href="/artikler/serienummer">Serienummeret</a> er','.</li>').strip()

    # motor
    motor_info = soup.find_all("table", class_="noheader")

    #kilometerhistorikk/eu-kontroll
    kilometerhistorikk = str(soup.find(id="kilometerhistorikk"))
    kmsoup = BeautifulSoup(kilometerhistorikk, 'html.parser')
    km = kmsoup.find_all("tr")

    eu_kontroll = {}
    for item in km:
        eu_kontroll[find(str(item), '<td style="color:;">', '</td>')] = find(str(item), '<td title="', '">')
    del eu_kontroll[""]
    eu = []
    for key,value in eu_kontroll.items():
        eu.append([value, key])

    # Mål og vekt
    maal_vekt = {}
    for t in motor_info[0]:
        maal_vekt[find(str(t), '<tr>\n<td>', '</td>').replace(" ", "_").lower()] = find(str(t), '</td>\n<td>', '</td>')
    del maal_vekt[""]

    # dekk felg
    dekk_felg={}
    for t in motor_info[2]:
        dekk_felg[find(str(t), '<tr>\n<td>', '</td>').replace(" ", "_").lower()] = find(str(t), '</td>\n<td>', '</td>')
    del dekk_felg[""]

    motor_info = str(motor_info[1])
    slagvolum = find(motor_info, "</sup><br/>", '</td>').strip()
    motorytelse = find(motor_info, '<td>Motorytelse</td>\n<td>','<br/>').strip()
    aksler_med_drift = find(motor_info, '<td>Aksler med drift</td>\n<td>','</td>').strip()

    kommentarer = soup.find_all("td")
    alle_kommentarer = []
    for kommentar in kommentarer:
        if "inline-kommentar-dato" in str(kommentar):
            kommentar = find(str(kommentar), "</b></span>", "</td>").strip()
            alle_kommentarer.append(kommentar)

    car_object = {  "kategori":kategori,
                    "type_bil": type_bil,
                    "tilhorer":tilhorer,
                    "info_politi":info_politi,
                    "slagvolum":slagvolum,
                    "motorytelse":motorytelse,
                    "aksler_med_drift":aksler_med_drift,
                    "serienummer": serienummer,
                    "kommentarer":alle_kommentarer,
                    "maal_vekt": maal_vekt,
                    "dekk_felg": dekk_felg,
                    "eu_kontroll": eu
                }

    jsonarray = json.dumps(car_object, indent=4, ensure_ascii=False)
    return jsonarray
# scrapeSingleSivil("BP99615")

@app.route('/normal/<regnr>')
def scrapeNormalCar(regnr):
    req = Request('https://regnr.info/' + regnr, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')

    # Check if car is stolen
    stolen = str(soup.find(id="warning-stolen"))
    if(stolen != None): #car is stolen
        stolen = find(str(stolen), "<h1>", "\n").strip()
    else:
        stolen = ""
    # kommentarer = soup.find_all("span", class_="inline-kommentar-dato")
    kjoretoy_info = str(soup.find_all("div", class_="kjoretoy-data"))
    kategori = find(kjoretoy_info, "<b>", "</b><br/>").strip()
    type_bil = find(kjoretoy_info, "<h1>","</h1>").strip()
    info_normal_eier = find(kjoretoy_info, '<div class="kjoretoy-data">\n<span>','</span></div>').strip()
    serienummer = find(str(soup.find_all("li")), '<a href="/artikler/serienummer">Serienummeret</a> er','.</li>').strip()

    motor_info = soup.find_all("table", class_="noheader")

    #kilometerhistorikk/eu-kontroll
    kilometerhistorikk = str(soup.find(id="kilometerhistorikk"))
    kmsoup = BeautifulSoup(kilometerhistorikk, 'html.parser')
    km = kmsoup.find_all("tr")

    eu_kontroll = {}
    for item in km:
        eu_kontroll[find(str(item), '<td style="color:;">', '</td>')] = find(str(item), '<td title="', '">')
    if "" in eu_kontroll:
        del eu_kontroll[""]
    eu = []
    for key,value in eu_kontroll.items():
        eu.append([value, key])

    # Mål og vekt
    maal_vekt = {}
    for t in motor_info[0]:
        maal_vekt[find(str(t), '<tr>\n<td>', '</td>').replace(" ", "_").lower()] = find(str(t), '</td>\n<td>', '</td>')
    del maal_vekt[""]

    # dekk felg
    dekk_felg={}
    for t in motor_info[2]:
        dekk_felg[find(str(t), '<tr>\n<td>', '</td>').replace(" ", "_").lower()] = find(str(t), '</td>\n<td>', '</td>')
    del dekk_felg[""]

    # motor
    motor_info = str(motor_info[1])
    slagvolum = find(motor_info, "</sup><br/>", '</td>').strip()
    motorytelse = find(motor_info, '<td>Motorytelse</td>\n<td>','<br/>').strip()
    aksler_med_drift = find(motor_info, '<td>Aksler med drift</td>\n<td>','</td>').strip()

    car_object = {
        "regnr": regnr,
        "stolen": stolen,
        "kategori": kategori,
        "type_bil": type_bil,
        "info_normal_eier": info_normal_eier,
        "serienummer": serienummer,
        "slagvolum": slagvolum,
        "motorytelse":motorytelse,
        "aksler_med_drift":aksler_med_drift,
        "maal_vekt": maal_vekt,
        "dekk_felg": dekk_felg,
        "eu_kontroll": eu
    }

    jsonarray = json.dumps(car_object, indent=4, ensure_ascii=False)
    return jsonarray
