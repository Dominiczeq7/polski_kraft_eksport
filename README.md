# Polski kraft eksport
Program służący do eksportu ocen z danego profilu na serwisie www.polskikraft.pl

## Wołanie:
pk_export.py --user_id <user_id> ?--file_name <file_name>? ?--bjcp_rating? ?--with_details?

## Objaśnienie:
--user_id: id profilu - można znaleźć będąc zalogowanym pod linkiem https://www.polskikraft.pl/profil/ (id dopisuje się na końcu adresu)

--file_name: opcjonalny parametr; nazwa pliku wyjściowego; plik zostanie zapisany w formacie CSV

--bjcp_rating: opcjonalny parametr; wybierz jeśli używałeś/aś zaawansowanego oceniania i chcesz zachować tą informację

--with_details: opcjonalny parametr; gdy jest użyty zbiera więcej informacji o piwach, natomiast jest to bardziej czasochłonne

## Wynik:
Wynikiem poprawnego zakończenia programu jest wygenerowanie pliku w formacie CSV w folderze z plikiem uruchomieniowym. Jeżeli został podany parametr --file_name to plik wynikowy będzie nosił nazwę <file_name>.csv, w przeciwnym wypadku [nazwa profilu]_pk_export.csv.
