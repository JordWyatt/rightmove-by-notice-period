import requests
import configparser
import datetime
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
from listing import Listing
from sheet import Sheet

config = configparser.ConfigParser()
config.optionxform = str
config.read("configuration.ini")

service_account_configuration_path = config.get(
    "gspread", "serviceAccountConfigurationPath")
sheet_name = config.get("gspread", "sheetName")


class RightmoveScraper:

    def __init__(self):
        self.base_url = "https://rightmove.co.uk"
        # Default to 24 hour period for now, don't show let agreed
        self.base_search_url = self.base_url + \
            "/property-to-rent/find.html?maxDaysSinceAdded=1&_includeLetAgreed=false&"
        self.sheet = Sheet(service_account_configuration_path, sheet_name)

    def build_search_url(self, location_identifier):
        parameters = config.items('filters')
        parameters.append(("locationIdentifier", location_identifier))
        search_url = self.base_search_url + urlencode(parameters)
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

    def get_location_name(self, dom):
        title = dom.title.string
        result = re.search(r".*Rent in (.*) \|", title)
        return result.group(1)

    def scrape(self, url):
        html = requests.get(url).text
        listing_dom = BeautifulSoup(html, 'html.parser')
        location = self.get_location_name(listing_dom)

        print(f"Scraping properties in {location}")

        listing_urls = self.get_listing_urls(listing_dom)
        listings = [Listing(url) for url in listing_urls]

        for listing in listings:
            listing.scrape_details()

        if(config.get("filters", "availableAfterNWeeks")):
            n_weeks = int(config.get("filters", "availableAfterNWeeks"))
            print(
                f'Filtering listings down only those available after {n_weeks} weeks from now')
            listings = self.get_listings_available_after_n_weeks(
                n_weeks, listings)

        return listings

    def remove_duplicate_listings(self, listings):
        unique = {}
        for listing in listings:
            if listing.url not in unique.keys():
                unique[listing.url] = listing
        return unique.values()

    def run(self):
        listings = []
        location_identifiers = config.get(
            "locations", "identifiers").split(",")

        for identifier in location_identifiers:
            url = self.build_search_url(identifier)
            listings.extend(self.scrape(url))

        if listings:
            unique_listings = self.remove_duplicate_listings(listings)
            write_results = self.sheet.add_listings(unique_listings)
            print(f"\nDone, { len(unique_listings) } properties were found")
            print(
                f"{write_results['written']} new properties were added to the worksheet {sheet_name}")
            print(
                f"{write_results['duplicates']} properties already existed on the sheet and were ignored")
        else:
            print("No listings found for specified search criteria")


if __name__ == '__main__':
    RightmoveScraper().run()
