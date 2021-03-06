Andre's Pricewatch
==================

(Hinweis: Deutschsprachige [README](README.de.md) verfügbar)

This little utility keeps an eye on the price of products in supported online shops.
If the price changes, an e-mail is sent out.

Shops included as of the time of writing:
- Amazon.de
- Saturn.de
- Mediamarkt.de (use Saturn.de provider in configuration file)

Set up a cron job to execute the script periodically. This will get you informed
whenever there is a price change.

A cache file is written to the disk with the last known price and the time of
request for every defined product section.

Besides the e-mail notification, output is also written to stdout:
Example:

```
SonyAlphaSaturn: provided price 629.00
SonyAlphaSaturn: Price has changed, new price: 629.0, old price: 639.0
SonyAlphaAmazon: provided price 600.9
Success: True
```

`Success` in this case is the overall success flag which considers the
requests of all sections. If one section fails, the flag is set to `False`.

# Python dependencies
- Python 3
- python-amazon-simple-product-api (pip install python-amazon-simple-product-api)
- requests
- Beautiful Soup 4

## Other requirements
A working e-mail server is needed to relay messages. You might have to adapt
the hard-coded server definition in the script file.

# Configuration file
See the included `pricewatch.ini-example` for a basic example of what can be done.

# Command line options

```
pricewatch.py [-h] [-c <config file>]

-h	prints the help
-c	set the path to the configuration file
```

If no configuration file is given, a `pricewatch.ini` file is searched in the script path.
