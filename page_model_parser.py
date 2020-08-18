import re
import json


class PageModelParser:
    def __init__(self, dom):
        self.page_data = self.get_page_data(dom)

    def get_page_data(self, dom):
        page_data = None
        pattern = re.compile('(.*)window.PAGE_MODEL = (.*)')
        scripts = dom.find_all('script')
        for script in scripts:
            scriptContent = str(script.string).strip()
            if(pattern.match(scriptContent)):
                match = pattern.match(scriptContent)
                page_data = json.loads(match.group(2))['propertyData']

        if not page_data:
            raise ValueError("Failed to retrieve page data")

        return page_data

    def get_price(self):
        return self.page_data['prices']['primaryPrice']

    def get_description(self):
        return self.page_data['text']['propertyPhrase']

    def get_address(self):
        return self.page_data['address']['displayAddress']

    def get_letting_information(self):
        information = self.page_data['lettings']

        letting_details = {
            "date_available": information.get("letAvailableDate"),
            "furnishing": information.get("furnishType"),
            "deposit": ''.join(("£", str(information.get("deposit")))) if information.get("deposit") else None
        }

        return letting_details

    def get_nearest_stations(self):
        stations = []
        station_data = self.page_data['nearestStations']

        for station in station_data:
            name = station['name']
            distance = str(station['distance'])[0:3]
            stations.append(name + " (" + distance + " mi)" "\n")

        return "".join(stations)
