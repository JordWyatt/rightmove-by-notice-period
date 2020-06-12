import requests
import configparser
import datetime
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
# Default to 24 hour period for now, don't show let agreed
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

    if(config["search"]["availableAfterNWeeks"]):
        n_weeks = int(config["search"]["availableAfterNWeeks"])
        print(
            f'Filtering listings down only those available after {n_weeks} weeks from now')
        listings = get_listings_available_after_n_weeks(n_weeks, listings)

    return listings


def get_listing_urls(soup):

    listings = soup.find_all("a", class_="propertyCard-rentalPrice")
    listing_urls = [base_url + listing.get("href")
                    for listing in listings if listing.get("href") != ""]
    return listing_urls


def get_listings_available_after_n_weeks(n_weeks, listings):

    def convert_date(x):
        return datetime.datetime.strptime(x, "%d/%m/%Y").date()

    today = datetime.datetime.now().date()
    delta = datetime.timedelta(weeks=n_weeks)
    available_after = (today + delta)
    return [listing for listing in listings if listing.has_date_available() and convert_date(listing.date_available) > available_after]


url = build_search_url()
listings = scrape(url)

if listings:
    sheet.add_listings(listings)

print(f"Done, { len(listings) } new properties were found")
