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

## Ajaminen

Komennolla

```
flask run
```

käynnistetään Flaskin devausympäristö, jossa verkkosivua voi kokeilla.
Oletuksena tietokanta luodaan automaattisesti tiedostoon `database.db`, jos sitä ei ole jo olemassa.
