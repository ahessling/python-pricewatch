Andre's Pricewatch
==================

Dieses kleine Skript beobachtet konfigurierte Produkte in unterstützten Online Webshops.
Wenn sich der Preis ändert, wird eine E-Mail ausgesendet.

Momentan unterstützte Shops:
- Amazon.de
- Saturn.de

Am besten setzt man einen cron job auf, damit das Skript periodisch ausgeführt wird.
So wird man informiert, sobald sich der Preis ändert.
Bitte aber nicht übertreiben und die Seiten zu häufig abfragen,
da dadurch unnötig viel Traffic und Rechenlast bei den Betreibern der Shops verursacht wird.

Die zuletzt gesehenen Preise pro Produkt mit Zeitstempel werden lokal auf die Festplatte
in eine Datei geschrieben.

Neben der E-Mail-Benachrichtigung gibt das Skript auch noch einige Ausgaben aus:
Beispiel:

```
SonyAlphaSaturn: provided price 629.00
SonyAlphaSaturn: Price has changed, new price: 629.0, old price: 639.0
SonyAlphaAmazon: provided price 600.9
Success: True
```

`Success` meint in diesem Fall das gesamte Ergebnis.
Wenn ein Produkt nicht abgefragt werden kann, wird das Flag sofort auf `False` gesetzt.

# Python Abhängigkeiten
- Python 3
- python-amazon-simple-product-api (pip install python-amazon-simple-product-api)
- requests
- Beautiful Soup 4

## Andere Abhängigkeiten
Ein funktionierender E-Mail-Server wird benötigt, um Nachrichten zu senden.
Die Einstellungen sind aktuell fest im Skript und müssen ggf. angepasst werden.

# Konfigurationsdatei
Ich verweise auf die mitgelieferte `pricewatch.ini-example` als ein einfaches Beispiel, umzu
zeigen, was prinzipiell gemacht werden kann.

# Kommandozeilenoptionen

```
pricewatch.py [-h] [-c <config file>]

-h	prints the help
-c	set the path to the configuration file
```

Wenn keine Konfigurationsdatei angegeben wird, wird eine `pricewatch.ini` im Skriptpfad gesucht.
