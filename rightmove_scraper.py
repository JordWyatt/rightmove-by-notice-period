import requests
import configparser
import datetime
import re
from textwrap import dedent
from mailer import Mailer
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
        if(not len(listings)):
            return listings

        print(
            f'Filtering listings down only those available after {n_weeks} weeks from now')

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

        print(f"Scraping properties in {location}...")

        listing_urls = self.get_listing_urls(listing_dom)
        listings = [Listing(url) for url in listing_urls]

        for listing in listings:
            listing.scrape_details()

        return listings

    def remove_duplicate_listings(self, listings):
        if(not len(listings)):
            return listings

        unique = {}
        for listing in listings:
            if listing.url not in unique.keys():
                unique[listing.url] = listing
        return unique.values()

    def filter_listings(self, listings):
        if(config.get("filters", "availableAfterNWeeks")):
            listings = self.get_listings_available_after_n_weeks(
                int(config.get("filters", "availableAfterNWeeks")), listings)
        return listings

    def scrape_listings(self, location_identifiers):
        listings = []
        for identifier in location_identifiers:
            url = self.build_search_url(identifier)
            listings.extend(self.scrape(url))

        listings = self.remove_duplicate_listings(listings)
        return listings

    def process_listings(self, listings):
        written, duplicates = self.sheet.add_listings(listings)
        message = dedent(f"""
                { len(listings) } eligible properties were found.
                {written} new properties were added to the worksheet {sheet_name}.
                {duplicates} properties already existed on the sheet and were ignored.
                """)
        print(message)

        if(config.has_section("mailer") and written):
            mailer_config = dict(config.items("mailer"))
            Mailer(mailer_config).send_mail(message)

    def run(self):
        location_identifiers = config.get(
            "locations", "identifiers").split(",")

        listings = self.filter_listings(
            self.scrape_listings(location_identifiers)
        )

        if(len(listings)):
            self.process_listings(listings)

        else:
            print("No listings found for specified search criteria")


if __name__ == '__main__':
    RightmoveScraper().run()
