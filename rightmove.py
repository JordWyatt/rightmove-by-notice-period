import requests
import configparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
from listing import Listing

config = configparser.ConfigParser()
config.optionxform = str
config.read("configuration.ini")
base_url = "https://rightmove.co.uk"
base_search_url = base_url + \
    "/property-to-rent/find.html?maxDaysSinceAdded=1&_includeLetAgreed=false&"


def build_search_url():
    params = urlencode(config['search'])
    search_url = base_search_url + params
    return search_url


def scrape(url):
    html = requests.get(url).text
    listing_dom = BeautifulSoup(html, 'html.parser')
    listing_urls = get_listing_urls(listing_dom)
    listings = [Listing(url) for url in listing_urls]
    scraped = enrich_listings(listings)


def get_listing_urls(soup):

    listings = soup.find_all("a", class_="propertyCard-rentalPrice")
    listing_urls = [base_url + listing.get("href")
                    for listing in listings if listing.get("href") != ""]
    return listing_urls


def enrich_listings(listings):
    eligible_listings = []

    for listing in listings:
        listing.scrape_details()
        eligible_listings.append(listing)

    return eligible_listings


url = build_search_url()
scrape(url)
