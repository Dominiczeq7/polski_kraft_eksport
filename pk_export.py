#########################################
# Name: Polski kraft eksport
# Author: Dominik Gąsienica-Gronikowski
# GitHub: https://github.com/Dominiczeq7
# License: GNU GPL v3.0
# Version: 1.0.0
#########################################

import urllib.request, sys, getopt, csv
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup as bso
from math import ceil
from time import time
from os import system, name

run_times = []

def clear_console():
    system('cls' if name=='nt' else 'clear')

def check_user_exists(user_id):
    user_url = "https://www.polskikraft.pl/profil/" + user_id
    user_exists = get_html_soup_object(user_url).find(id="sf-resetcontent") is None
    return user_exists

def get_user_name(user_id):
    user_url = "https://www.polskikraft.pl/profil/" + user_id
    user_name = get_html_soup_object(user_url).find(class_="pk-user-profile-name").contents[0].strip()
    return user_name

def set_columns(bjcp_rating, with_details):
    csv_columns = {
        "name": "Piwo",
        "style": "Styl",
        "brewery": "Browar",
        "mean_score": "Średnia ocena",
        "checkin_date": "Data wpisu",
        "checkin_rating": "Moja ocena",
        "checkin_comment": "Mój komentarz"
    }
    if bjcp_rating:
        csv_columns["rate_smell"] = "Ocena: aromat (maks 12)"
        csv_columns["rate_look"] = "Ocena: wygląd (maks 3)"
        csv_columns["rate_taste"] = "Ocena: smak (maks 20)"
        csv_columns["rate_mouthfeel"] = "Ocena: odczucie w ustach (maks 5)"
        csv_columns["rate_overall"] = "Ocena: ogólne wrażenie (maks 10)"
    if with_details:
        csv_columns["beer_extract"] = "Ekstrakt"
        csv_columns["alcohol"] = "Alkohol"
        csv_columns["ibu"] = "IBU"
        csv_columns["detailed_style"] = "Szczegółowy styl"
        csv_columns["hops"] = "Chmiele"
        csv_columns["malts"] = "Słody"
        csv_columns["yeast"] = "Drożdże"
        csv_columns["other_extras"] = "Inne dodatki"
        csv_columns["description"] = "Opis"
    return csv_columns

def get_number_ratings(user_id):
    user_url = "https://www.polskikraft.pl/profil/" + user_id
    rating_section = get_html_soup_object(user_url).find(class_="col-lg-7 col-sm-6 col-xs-12")
    rating_header = rating_section.find(class_="row headline-min").get_text()
    parse_number = "".join(filter(str.isdigit, rating_header))
    
    return parse_number

def beautify_text(text):
    if isinstance(text, str):
        return text.strip().replace(';', '.').replace('\n', ' ')
    else:
        return text

def change_empty_sign(text):
    if text == "-":
        return ""
    else:
        return text
  
def write_to_csv(file_name, columns, data):
    try:
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, columns.keys(), delimiter=';')
            writer.writerow(columns)
            writer.writerows(data)
            
        print("Zapisano do pliku " + file_name)
    except IOError:
        print("Błąd wejścia/wyjścia!")
    
def get_html_soup_object(url):
    try:
        fp = urllib.request.urlopen(url)
        mybytes = fp.read()
        fp.close()
    except HTTPError as e:
        mybytes = e.read()
    except URLError:
        print("Błąd sieci! Upewnij się czy działa połączenie z internetem.")
        sys.exit(2)
        
    html = mybytes.decode("utf8")
        
    return bso(html, "html.parser")

def get_beer_data(beer_checkin, bjcp_rating, with_details):
    name = beer_checkin.find("h4").get_text()
    brewery_and_style = beer_checkin.find("p").get_text()
    brewery, style = brewery_and_style.split(" | ")
    date = beer_checkin.find(class_="date").get_text()
    mean_score = beer_checkin.find(class_="row global-rating").find("p").get_text()
    comment = beer_checkin.find(class_="text").get_text()
    
    rating_section = beer_checkin.find(class_="star-rating")
    stars = rating_section.find_all(class_="fa fa-star fa-lg")
    rating = len(stars)
    
    checkin_data = {
        "name": name,
        "style": style,
        "brewery": brewery,
        "mean_score": mean_score,
        "checkin_date": date,
        "checkin_rating": rating,
        "checkin_comment": comment
    }
    
    if bjcp_rating:
        bjcp_section = beer_checkin.find_all(class_="row pk-comments-bjcp-bar")
        info_dict = {
            "AROMAT": "rate_smell",
            "WYGLĄD": "rate_look",
            "SMAK": "rate_taste",
            "ODCZUCIE W USTACH": "rate_mouthfeel",
            "OGÓLNE WRAŻENIE": "rate_overall"
        }
        
        for column_name in info_dict.values():
            checkin_data[column_name] = ""
        
        for rate in bjcp_section:
            rate_name = rate.find(class_="title").get_text()
            rate_value = rate.find(class_="rating").get_text().split('/')[0]
            if rate_name in info_dict:
                checkin_data[info_dict[rate_name]] = rate_value

    
    if with_details:
        beer_link = beer_checkin["href"]
        beer_details = get_html_soup_object(beer_link).find(class_="panel-body pk-panel-tile")
        
        beer_extract = change_empty_sign(beer_details.find(id="amount-blg-s").get_text())
        alcohol = change_empty_sign(beer_details.find(id="amount-alc-s").get_text())
        ibu = change_empty_sign(beer_details.find(id="amount-ibu-s").get_text())
        description = beer_details.find(class_="description").get_text()
        
        beer_info = beer_details.find_all(class_="col-xs-12 pk-details-category")
        info_dict = {
            "STYL": "detailed_style",
            "CHMIELE": "hops",
            "SŁODY": "malts",
            "DROŻDŻE": "yeast",
            "INNE DODATKI": "other_extras"
        }
        
        for column_name in info_dict.values():
            checkin_data[column_name] = ""
        
        for detail in beer_info:
            detail_name = detail.find("h3").get_text()
            detail_value = detail.find("p").get_text()
            if detail_name in info_dict:
                checkin_data[info_dict[detail_name]] = detail_value
        
        checkin_data["beer_extract"] = beer_extract
        checkin_data["alcohol"] = alcohol
        checkin_data["ibu"] = ibu
        checkin_data["description"] = description
    
    for key, value in checkin_data.items():
        checkin_data[key] = beautify_text(value)
        
    return checkin_data

def get_download_stats(number_of_ratings, actual_number_of_checkins, counts_on_page, start_time, page):
    clear_console()
    division = 20
    if actual_number_of_checkins < number_of_ratings:
        circuit_limit = ceil(number_of_ratings / counts_on_page)
        print("Pobieranie ocen: {0}/{1}".format(actual_number_of_checkins, number_of_ratings))
        
        stage_points = int(actual_number_of_checkins / number_of_ratings * division)
        print("[", end='')
        for i in range(stage_points):
            print("#", end='')
        for i in range(division - stage_points):
            print(" ", end='')
        print("]")
        
        run_time = float(time() - start_time)
        run_times.append(run_time)
        mean_time = sum(run_times) / len(run_times) 
        time_to_end = int(mean_time * (circuit_limit - page))
        minutes = int(time_to_end / 60)
        seconds = time_to_end % 60
        print("Pozostało około ", end='')
        if minutes != 0:
            print(str(minutes) + " minut i ", end='')
        print(str(seconds) + " sekund.")
    else:
        print("Pobrano {0} ocen".format(actual_number_of_checkins))
        print("[", end='')
        for i in range(division):
            print("#", end='')
        print("]")

def get_checkins_data(user_id, bjcp_rating, with_details, number_of_ratings):
    checkins_data = []
    page = 1
    while(1):
        url = "https://www.polskikraft.pl/ajax/user/" + user_id + "/comments/newest/" + str(page)
        
        start_time = time()
            
        beer_checkins = get_html_soup_object(url).find_all(class_ = "pk-profile-comment-link")
        if not beer_checkins:
            break
        
        checkins_count_before = len(checkins_data)
        for beer_checkin in beer_checkins:
            checkin_data = get_beer_data(beer_checkin, bjcp_rating, with_details)
            checkins_data.append(checkin_data)
        checkins_count_after = len(checkins_data)
        added_checkins = checkins_count_after - checkins_count_before
        
        page += 1
        get_download_stats(number_of_ratings, len(checkins_data), added_checkins, start_time, page)
        
        # break
    
    get_download_stats(number_of_ratings, number_of_ratings, len(checkin_data), start_time, page)
    
    return checkins_data
    
 
def main(argv):
    user_id = ""
    file_name = ""
    with_details = 0
    bjcp_rating = 0
    clear_console()
    
    try:
       opts, args = getopt.getopt(argv,"hu:f:bw",["help","user_id=","file_name=","bjcp_rating=","with_details="])
    except getopt.GetoptError:
       print("Prawidłowe wołanie:")
       print("pk_export.py --user_id <user_id> ?--file_name <file_name>? ?--bjcp_rating? ?--with_details?")
       print("Więcej informacji pod komendą --help")
       sys.exit(2)
       
    for opt, arg in opts:
       if opt in ("-h" "--help"):
          print("Wołanie:")
          print("pk_export.py --user_id <user_id> ?--file_name <file_name>? ?--bjcp_rating? ?--with_details?")
          print("\nObjaśnienie:")
          print("--user_id: id profilu - można znaleźć będąc zalogowanym pod linkiem https://www.polskikraft.pl/profil/ (id dopisuje się na końcu adresu)")
          print("--file_name: opcjonalny parametr; nazwa pliku wyjściowego; plik zostanie zapisany w formacie CSV")
          print("--bjcp_rating: opcjonalny parametr; wybierz jeśli używałeś/aś zaawansowanego oceniania i chcesz zachować tą informację")
          print("--with_details: opcjonalny parametr; gdy jest użyty zbiera więcej informacji o piwach, natomiast jest to bardziej czasochłonne")
          print("\nWynik:")
          print("Wynikiem poprawnego zakończenia programu jest wygenerowanie pliku w formacie CSV w folderze z plikiem uruchomieniowym. \
Jeżeli został podany parametr --file_name to plik wynikowy będzie nosił nazwę <file_name>.csv, w przeciwnym wypadku \
[nazwa profilu]_pk_export.csv.")
          sys.exit()
       elif opt in ("-u" "--user_id"):
          user_id = arg
       elif opt in ("-f" "--file_name"):
          file_name = arg
       elif opt in ("-w", "--with_details"):
          with_details = 1
       elif opt in ("-b", "--bjcp_rating"):
          bjcp_rating = 1
          
    if not opts:
        user_id = input("Podaj id profilu: ")
        
    if user_id == "":
        print("Paremetr --user_id jest obowiązkowy!")
        sys.exit(2)
    elif not user_id.isdigit():
        print("user_id musi być cyfrą!")
        sys.exit(2)
    elif not check_user_exists(user_id):
        print("Użytkownik o podanym id nie istnieje!")
        sys.exit(2)
        
    print("Rozpoczynanie pobierania...")
    
    if file_name == "":
        file_name = get_user_name(user_id) + "_pk_export"
    csv_file_name = file_name + ".csv"
    
    number_of_ratings = get_number_ratings(user_id)
    
    if (number_of_ratings != 0):
        checkins_data = get_checkins_data(user_id, bjcp_rating, with_details, int(number_of_ratings))
        
        csv_columns = set_columns(bjcp_rating, with_details)
        write_to_csv(csv_file_name, csv_columns, checkins_data)
    else:
        "Brak ocen."
    

if __name__ == "__main__":
    main(sys.argv[1:])
    