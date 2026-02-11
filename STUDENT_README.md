# Ohjeet harjoitukseen

Tervetuloa! Tämä ohje kertoo, miten komentoriviharjoituksia tehdään ja miten ajat harjoitusohjelman ja miten lähetät tulokset GitHub Classroomiin.

## Harjoittelu paikallisesti
Yritä ratkaista annetut tehtävät ensin komentoriviä käyttäen. Harjoituksissa käytettävät tiedostot löytyvät hakemistosta nimeltä `data`. Harjoitusten oikeat vastaukset saat testattua ajamalla sovelluksen jonka käyttö kuvataan alla. Sitä kannattaa ajaa esim. toisessa terminaalissa.

## Sovelluksen ajaminen paikallisesti
Interaktiivinen harjoitus käynnistyy kommennolla:

```bash
python3 harjoitus.py
```

Ohjelma näyttää tehtävän kuvauksen ja pyytää sinua syöttämään Linux-komennon, joka tuottaa halutun tulosteen. Voit yrittää ratkaista tehtäviä niin monta kertaa kuin haluat.

Kun suoritat komennon, ohjelma vertailee komentosi tuottamia tuloksia oikeaan vastaukseen. Samaan lopputulokseen voi päästä monella eri komennolla.

Oikean vastauksen jälkeen saat seuraavan tehtävän näkyviin. Jos haluat hypätä tehtävän yli, voit antaa komennon `skip`. Komennolla `lista` näet jäljelläolevat tehtävät. Komento `exit` lopettaa kyselyn. Oikeat vastaukset tallentuvat järjestelmään ja voit jatkaa harjoittelua käynnistämällä sovelluksen uudestaan.

Komennot:
- `skip` — siirry seuraavaan tehtävään
- `lista` — näytä tehtävien tila
- `exit` — tallenna tila ja poistu



## Tulosten lähettäminen GitHub Classroomiin

Kun olen saanut ratkaistua kaikki haluamasi tehtävät voit lähettää ne Github Classroomiin tilastointia varten.

Tämä tapahtuu antamalla seuraavat komennot terminaalissa:

```bash
git checkout -b my/solution
git add output/results.json
git commit -m "Lisää harjoituksen tulos"
git push origin my/solution
```


## Tukea saatavilla
Jos tarvitset apua tehtävissä kysy opettajalta.

*** Onnea harjoituksiin! ***
