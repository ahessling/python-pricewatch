import requests
import configparser
from bs4 import BeautifulSoup
from time import gmtime, strftime
import smtplib
from email.mime.text import MIMEText
from amazon.api import AmazonAPI
import os, sys, getopt
import socket, getpass

def provider_saturn(section):
	"""Provider for Saturn.de
	"""

	try:
		url_request = requests.get(section['url'])
		soup = BeautifulSoup(url_request.text, "lxml")

		result = soup.find(property="product:price:amount")

		if not (result is None):
	        	return result.get('content')
		else:
			return None

	except:
		return None

def provider_amazon_de(section):
	"""Provider for Amazon
	"""

	try:
		amazon = AmazonAPI(section['amazon_access_key'], section['amazon_secret_key'], section['amazon_assoc_tag'], region="DE")
		product = amazon.lookup(ItemId=section['asin'])
		
		return product.price_and_currency[0]
	except:
		return None

def write_to_db(dbcache, section, items, price):
	"""Update price entry in DB cache file
	"""

	if not dbcache.has_section(section):
		dbcache.add_section(section)

	dbcache.set(section, "currentprice", str(price))
	dbcache.set(section, "lastchecked", strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

	return

def check_price(dbcache, section, items, price):
	"""Check for price change and set notify flags accordingly.
	"""

	# price must have been previously set
	try:
		lastprice = float(dbcache.get(section, "currentprice"))
	except:
		lastprice = None

	# price: str to float
	try:
		price = float(price)
	except:
		price = None

	# sanity check
	if not 'notify' in items:
		print("Notify method not set in config file!", file=sys.stderr)
		exit(-1)

	# price available now, but not before
	if (not (price is None)) and (lastprice is None):
		return {'Notify': True, 'Reason': 'Now available', 'Lastprice': lastprice, 'Price': price}

	# price available before, but not now (error?)
	if (not (lastprice is None)) and (price is None):
		return {'Notify': True, 'Reason': 'Not available anymore', 'Lastprice': lastprice, 'Price': price}

	# check if price has changed
	if price != lastprice:
		if items["notify"] == "price_changed":
			return {'Notify': True, 'Reason': 'Price has changed', 'Lastprice': lastprice, 'Price': price}
		elif items["notify"] == "price_lower":
			if price < lastprice:
				return {'Notify': True, 'Reason': 'Price is lower', 'Lastprice': lastprice, 'Price': price}
		else:
			print("Unknown notify method: " + items["notify"], file=sys.stderr)
			exit(-1)
	# no change
	return {'Notify': False, 'Reason': 'Price not changed', 'Lastprice': lastprice, 'Price': price}

def notify_price(email_to, section, check_price_result):
	message = section + ": " + check_price_result['Reason'] + ", new price: " + str(check_price_result['Price']) + ", old price: " + str(check_price_result['Lastprice'])

	print(message)

	# send email
	if not (email_to is None):
		email_msg = MIMEText(message)
		email_msg['Subject'] = "pricewatch update: " + section
		email_msg['From'] = getpass.getuser() + "@" + socket.getfqdn()
		email_msg['To'] = email_to
		s = smtplib.SMTP('localhost')
		s.send_message(email_msg)
		s.quit()

def iterate_sections(config):
	Success = True

	# open cache file
	try:
		dbcachefilename = config.defaults()['dbfile']
	except:
		print("Could not find entry dbfile in settings", file=sys.stderr)
		exit(-1)

	dbconfig = configparser.ConfigParser()
	dbconfig.read(dbcachefilename)

	for section in config.sections():
		retries = config.getint(section, "retries", fallback=1)
		retry = 0
		price = None

		while retry < retries and price is None:
			# tuple-list --> dict
			dict_section = dict(config.items(section))

			provider = config.get(section, "provider")

			if provider == "saturn.de":
				price = provider_saturn(dict(config.items(section)))
			elif provider == "amazon.de":
				price = provider_amazon_de(dict(config.items(section)))
			else:
				print("Provider " + provider + " not found", file=sys.stderr)
				exit(-1)

		if not (price is None):
			print(section + ": provided price " + str(price))
		else:
			print(section + ": Could not get price!", file=sys.stderr)
			Success = False

		# check price
		check_price_result = check_price(dbconfig, section, dict_section, price)
		
		# make the notification
		if check_price_result['Notify'] == True:
			notify_price(config.get(section, "email"), section, check_price_result)

		# update cache entry in db file
		write_to_db(dbconfig, section, dict_section, price)

	# write db file to disk
	with open(dbcachefilename, 'w') as dbfile:
		dbconfig.write(dbfile)

	return Success

def main(argv):
	# open config file
	config = configparser.ConfigParser()

	# get script path
	source_dir = os.path.dirname(os.path.abspath(__file__))

	# default filename of config
	config_filename = source_dir + '/pricewatch.ini'

	# parse command line options
	try:
		opts, args = getopt.getopt(argv,"hc:",["config="])
	except getopt.GetoptError:
		print('pricewatch.py [-h] [-c <config file>]')
		exit(2)

	for opt, arg in opts:
		if opt in ("-c", "--config"):
			config_filename = arg
		elif opt == '-h':
			print('pricewatch.py [-h] [-c <config file>]')
			exit(0)

	if config.read(config_filename) == []:
		print("configuration file not found", file=sys.stderr)
		exit(-1)

	# iterate over all sections
	Success = iterate_sections(config)

	print("Success: " + str(Success))

	if Success == True:
		exit(0)
	else:
		print("Could not get price for at least one section", file=sys.stderr)
		exit(-1)

if __name__ == "__main__":
   main(sys.argv[1:])
