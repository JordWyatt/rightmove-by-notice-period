import requests
import configparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
from listing import Listing
from sheet import Sheet

config = configparser.ConfigParser()
config.optionxform = str
config.read("configuration.ini")

service_account_configuration_path = config["gspread"]["serviceAccountConfigurationPath"]
sheet_name = config["gspread"]["sheetName"]
sheet = Sheet(service_account_configuration_path, sheet_name)

base_url = "https://rightmove.co.uk"
base_search_url = base_url + \
    "/property-to-rent/find.html?maxDaysSinceAdded=1&_includeLetAgreed=false&"


def build_search_url():
    params = urlencode(config['search'])
    search_url = base_search_url + params
    return search_url


def scrape(url):
    print("Retrieving eligible properties...")
    html = requests.get(url).text
    listing_dom = BeautifulSoup(html, 'html.parser')
    listing_urls = get_listing_urls(listing_dom)
    listings = [Listing(url) for url in listing_urls]

    for listing in listings:
        listing.scrape_details()

    return listings


def get_listing_urls(soup):

    listings = soup.find_all("a", class_="propertyCard-rentalPrice")
    listing_urls = [base_url + listing.get("href")
                    for listing in listings if listing.get("href") != ""]
    return listing_urls


url = build_search_url()
listings = scrape(url)
if listings:
    sheet.add_listings(listings)

print(f"Done, { len(listings) } new properties were found")
