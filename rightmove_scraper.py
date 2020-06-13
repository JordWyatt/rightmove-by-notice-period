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


class RightmoveScraper:

    def __init__(self):
        self.base_url = "https://rightmove.co.uk"
        # Default to 24 hour period for now, don't show let agreed
        self.base_search_url = self.base_url + \
            "/property-to-rent/find.html?maxDaysSinceAdded=1&_includeLetAgreed=false&"
        self.sheet = Sheet(service_account_configuration_path, sheet_name)

    def build_search_url(self):
        params = urlencode(config['search'])
        search_url = self.base_search_url + params
        return search_url

    def get_listing_urls(self, soup):

        listings = soup.find_all("a", class_="propertyCard-rentalPrice")
        listing_urls = [self.base_url + listing.get("href")
                        for listing in listings if listing.get("href") != ""]
        return listing_urls

    def get_listings_available_after_n_weeks(self, n_weeks, listings):

        def convert_date(x):
            return datetime.datetime.strptime(x, "%d/%m/%Y").date()

        today = datetime.datetime.now().date()
        delta = datetime.timedelta(weeks=n_weeks)
        available_after = (today + delta)
        return [listing for listing in listings if listing.has_date_available() and convert_date(listing.date_available) > available_after]

    def scrape(self, url):
        print("Retrieving eligible properties...")
        html = requests.get(url).text
        listing_dom = BeautifulSoup(html, 'html.parser')
        listing_urls = self.get_listing_urls(listing_dom)
        listings = [Listing(url) for url in listing_urls]

        for listing in listings:
            listing.scrape_details()

        if(config["search"]["availableAfterNWeeks"]):
            n_weeks = int(config["search"]["availableAfterNWeeks"])
            print(
                f'Filtering listings down only those available after {n_weeks} weeks from now')
            listings = self.get_listings_available_after_n_weeks(
                n_weeks, listings)

        return listings

    def run(self):
        url = self.build_search_url()
        listings = self.scrape(url)

        if listings:
            write_results = self.sheet.add_listings(listings)
            print(f"Done, { len(listings) } properties were found")
            print(
                f"{write_results['written']} new properties were added to the worksheet {sheet_name}")
            print(
                f"{write_results['duplicates']} duplicate properties were ignored")
        else:
            print("No listings found for specified search criteria")


if __name__ == '__main__':
    RightmoveScraper().run()
