import requests, bs4
import json


def car_information(regnr):        
    r = requests.get('https://www.vegvesen.no/kjoretoy/kjop+og+salg/kj%C3%B8ret%C3%B8yopplysninger?registreringsnummer='+regnr)
    soup = bs4.BeautifulSoup(r.text, 'lxml')
    contents = soup.find(class_='text')
    car_object = {}
    for table in contents.find_all(class_='definisjonsliste'):
        titles = table.find_all("dt")
        data = table.find_all("dd")
        for item in range(len(data)):
            car_object[titles[item].text.strip().replace(" ", "_").replace("-","_").replace("å","a").replace("ø","o").replace(".","_").replace("/","_").lower()] = data[item].text.strip()
    return json.dumps(car_object, indent=4, ensure_ascii=False)


print(car_information("BT10668"))



# data = json.load(open("all.json"))
# d = []
# for i in range(len(data)):
#     regnr = data[i]["regnr"]
#     if regnr:
#         new_car = json.loads(car_information(regnr))
#         if new_car:
#             new_car["picture"] = data[i]["picture"]
#         else:
#             new_car = data[i]
#     d.append(new_car)

# with open("new_car.json", "w") as file:
#     json.dump(d, file)
        



