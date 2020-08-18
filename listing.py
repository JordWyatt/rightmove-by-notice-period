import requests
from html_parser import HtmlParser
from page_model_parser import PageModelParser
from bs4 import BeautifulSoup
from datetime import date


class Listing:
    def __init__(self, url):
        self.url = url

    def get_dom(self):
        html = requests.get(self.url).text
        return BeautifulSoup(html, "html.parser")

    def get_parser(self, dom):
        lettingInformationDiv = dom.find("div", id="lettingInformation")

        if lettingInformationDiv:
            return HtmlParser(dom)
        else:
            return PageModelParser(dom)

    def scrape_details(self):
        dom = self.get_dom()
        parser = self.get_parser(dom)

        self.date_scraped = date.today().strftime('%d/%m/%Y')
        self.description = parser.get_description()
        self.price = parser.get_price()
        self.location = parser.get_address()
        self.nearest_stations = parser.get_nearest_stations()

        letting_information = parser.get_letting_information()

        self.date_available = letting_information.get("date_available")
        self.furnished = letting_information.get("furnishing")
        self.deposit = letting_information.get("deposit")

    def has_date_available(self):
        if self.date_available and self.date_available != "Now":
            return True

        return False
