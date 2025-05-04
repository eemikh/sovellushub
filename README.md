# SovellusHub

SovellusHub on verkkosivusto, jolla voi jakaa itse tekemiään avoimen lähdekoodin ohjelmia.
Sivusto toimii lähinnä mainossivustona, jolla voi mainostaa tekemiään ohjelmia ja löytää muiden
tekemiä kiinnostavia ohjelmia.
Sivusto ei itse tallenna mitään koodia tai tiedostoja, vaan linkit näihin.

Käyttäjä voi luoda sovelluksia, joilla on nimi, kuvaus ja linkki lähdekoodiin ja lataukseen tai
muualle, missä sovellusta voi käyttää (esim. verkkosivu).
Sovelluksen sivulla käyttäjä voi arvostella sovelluksen kommentilla ja arvosanalla 1-5.
Sovelluksen arvosanojen keskiarvosta lasketaan sovelluksen arvosana.
Sovelluksille voidaan määrittää sovelluksen tyypin mukaan luokkia, kuten komentorivin ohjelma,
Linux, verkkosivu, tms.
Sivustolla voi hakea sovelluksia nimen ja kuvauksen perusteella.
Käyttäjäsivulta näkee käyttäjän jakamat sovellukset ja niiden määrän.

## Välipalautus 2

Sivustolla toimivat kaikki yllä kuvatut ominaisuudet paitsi luokkien määrittäminen sovellukselle.
Koodia on tehty funktionaalisuus tärkeimpänä prioriteettina, ja luokkien lisäämisen jälkeen koodin
parannus ja verkkosivun parempi tyylittely ja käytettävyys on seuraava vaihe.
Myös voisi olla järkevää mahdollistaa arvostelujen muokkaaminen.

## Välipalautus 3

Kaikki välipalautuksen 2 kommentit yllä vielä pätevät, paitsi nyt kaikki ominaisuudet toimivat, myös
luokkien määrittäminen.
Käytettävyyttä parantavia ominaisuuksia, kuten arvosteluiden muokkaaminen ja sovelluksen luokkien
muokkaaminen, olisi hyvä lisätä.
Myös koodin laatua ja tyyliohjeiden noudattavuutta olisi syytä parantaa ennen viimeistä palautusta.

## Lopullinen palautus

Lopullinen sovellus on kuin ylhäällä alun perin kuvailtu. Joitain pieniä käytettävyysominaisuuksia
puuttuu, mutta suurempia käytettävyysongelmia ei ole sovelluksessa.

## Ajaminen

Komennolla

```
flask run
```

käynnistetään Flaskin devausympäristö, jossa verkkosivua voi kokeilla.
Oletuksena tietokanta luodaan automaattisesti tiedostoon `database.db`, jos sitä ei ole jo olemassa.

## Suorituskyky

Komento

```
python seed.py
```

lisää tietokantaan automaattisesti 10 000 käyttäjää, joista jokaisella on keskimäärin 250 ohjelmaa
ja 500 arvostelua satunnaisissa ohjelmissa. Kokeilin tällaisella tietokannalla eri sivujen
lataamisen nopeuksia. Kun ladataan etusivu sivulla 100 000, sivu latautuu 0,19 sekunnissa.
Satunnaisesti valitun käyttäjäsivun viimeisen sivun lataaminen kestää 0,01 sekuntia. Hakeminen
hakusanalla "linux" onnistuu 0,0 sekunnissa ja viimeinen sivu (tässä tapauksesas 6967) latautuu 0,62
sekunnissa.
