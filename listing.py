import requests
from bs4 import BeautifulSoup
from datetime import date


class Listing:
    def __init__(self, url):
        self.url = url

    def get_dom(self):
        html = requests.get(self.url).text
        return BeautifulSoup(html, "html.parser")

    def scrape_details(self):
        dom = self.get_dom()

        letting_information = self.get_letting_information(dom)
        self.date_scraped = date.today().strftime('%m/%d/%Y')
        self.description = self.get_description(dom)
        self.price = self.get_price(dom)
        self.location = self.get_address(dom)
        self.nearest_stations = self.get_nearest_stations(dom)
        self.date_available = letting_information.get("date_available")
        self.furnished = letting_information.get("furnishing")
        self.deposit = letting_information.get("deposit")

    def get_price(self, dom):
        return dom.find("p", id="propertyHeaderPrice").strong.contents[0].replace(
            "\n", "").replace("\t", "").replace("\r", "")

    def get_description(self, dom):
        name = dom.find("h1", itemprop="name").string
        description = name.split("to rent", 1)[0]
        return description

    def get_address(self, dom):
        address = dom.find(
            "meta", itemprop="streetAddress").get("content")
        return address

    def get_letting_information(self, dom):

        letting_details = {}

        rows = dom.find(
            "div", id="lettingInformation").find("tbody").find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            key = cells[0].string.replace(":", "")
            value = cells[1].string
            if key == "Date available":
                letting_details["date_available"] = value
            elif key == "Furnishing":
                letting_details["furnishing"] = value
            elif key == "Deposit":
                letting_details["deposit"] = value

        return letting_details

    def get_nearest_stations(self, dom):
        stations = []
        station_list = dom.find(
            "ul", class_="stations-list").find_all("li")

        for li in station_list:
            station = li.find("span").string
            distance = li.find("small").string
            stations.append(station + " " + distance + "\n")

            # Using strings for now, easier with gspread
            #stations.append((station, distance))

        return "".join(stations)

    def has_date_available(self):
        if self.date_available and self.date_available != "Now":
            return True

        return False
