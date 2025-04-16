# Street-racer
Street-Racer je aplikacija za mestne dirke (mogoče ilegalne... kdo bi vedel?), kjer se uporabniki pomerijo za naslov najboljšega voznika. Uporabnik se lahko prijavi v aplikacijo z uporabniškim imenom in geslom ali pa se registrira, kjer vnese svoje ime in priimek, izbere svoj avto ter si določi vzdevek oziroma uporabniško ime.

Ko je uporabnik prijavljen, lahko pogleda svoj profil, kjer so vidni njegovi podatki, izbrani avto ter število zbranih točk. Poleg tega lahko uporabnik pogleda vse razpoložljive dirke in se na željeno dirko prijavi. Če se premisli, se lahko z dirke tudi odjavi. Uporabnik ima vedno vpogled v rezultate preteklih dirk, lahko spremlja trenutno stanje lestvice championshipa ter pogleda svojo statistiko in napredek.

Administrator ima dostop do istih funkcionalnosti kot običajen uporabnik, poleg tega pa ima še dodatne možnosti. Administrator lahko po končani dirki vnese rezultate dirke, pri čemer se točke uporabnikom avtomatsko preračunajo in se posodobijo tako rezultati posameznih dirk kot tudi skupna championship lestvica. Poleg tega lahko administrator doda nove administratorje v sistem.

Za testiranje aplikacije lahko uporabite naslednje uporabniške račune:

Za prijavo kot navaden uporabnik uporabite uporabniško ime: uporabnik in geslo: geslo.

Za prijavo kot administrator uporabite uporabniško ime: admin in geslo: geslo.

Aplikacijo lahko zaženete preko Binderja: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/MateoVrtunski/Street-racer/main?urlpath=proxy%2F8080).

Spodaj se nahaja tudi ER diagram podatkovne baze, ki prikazuje povezave med entitetami in njihovo strukturo. (To je prvotni ER diagram in ni ČISTO tak kot je aplikacija).

![alt text](https://github.com/MateoVrtunski/Street-racer/blob/main/Street_racer.drawio.png?raw=true)
 
Še nekaj splošnih pravil: maksimalno število ljudi za eno dirko je 20, dve osebi nemoreta imeti enako uporabniško ime, nemoremo vpisati rezultatov, če ni vsaj 10 prijavljenih.
Ko dodamo osebo za admin, je ta zbrisana iz uporabnikov (geslo ima še vedno isto), za admina lahko izberemo samo osebo, ki ni prijavljena na nobeno dirko.

Srečno pot!

