# Elections Scraper

Třetí projekt do Engeto Online Python Akademie.

## Popis projektu

Program stahuje výsledky voleb do Poslanecké sněmovny z roku 2017 z webu
[volby.cz](https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ). Pro zvolený
územní celek projde všechny jeho obce a jejich výsledky uloží do CSV souboru.

## Instalace knihoven

Knihovny potřebné ke spuštění jsou uložené v souboru `requirements.txt`.
Doporučuji je nainstalovat do nového virtuálního prostředí:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Spuštění projektu

Program se spouští s **dvěma povinnými argumenty**:

```
python3 main.py <odkaz-na-uzemni-celek> <vystupni-soubor.csv>
```

1. odkaz na územní celek ze sloupce „Výběr obce“ (symbol `X`)
   na stránce volby.cz,
2. název výstupního souboru s příponou `.csv`.

Pokud některý argument chybí nebo není ve správném tvaru, program vypíše
upozornění a skončí.

## Ukázka projektu

Výsledky hlasování pro okres Prostějov:

```
python3 main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" vysledky_prostejov.csv
```

Průběh stahování:

```
STAHUJI DATA Z VYBRANÉHO URL: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
UKLÁDÁM DO SOUBORU: vysledky_prostejov.csv
UKONČUJI election-scraper
```

Částečný výstup:

```
code,location,registered,envelopes,valid,Občanská demokratická strana,...
506761,Alojzov,205,145,144,29,...
589268,Bedihošť,834,527,524,51,...
```

## Výstupní soubor

Každý řádek CSV souboru odpovídá jedné obci a obsahuje:

- kód obce,
- název obce,
- voliče v seznamu,
- vydané obálky,
- platné hlasy,
- počet hlasů pro každou kandidující stranu (co sloupec, to strana).
