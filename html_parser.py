class HtmlParser:
    def __init__(self, dom):
        self.dom = dom

    def get_price(self):
        return self.dom.find("p", id="propertyHeaderPrice").strong.contents[0].replace(
            "\n", "").replace("\t", "").replace("\r", "")

    def get_description(self):
        name = self.dom.find("h1", itemprop="name").string
        description = name.split("to rent", 1)[0]
        return description

    def get_address(self):
        address = self.dom.find(
            "meta", itemprop="streetAddress").get("content")
        return address

    def get_letting_information(self):
        letting_details = {}
        rows = self.dom.find(
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

    def get_nearest_stations(self):
        stations = []
        station_list = self.dom.find(
            "ul", class_="stations-list").find_all("li")

        for li in station_list:
            station = li.find("span").string
            distance = li.find("small").string
            stations.append(station + " " + distance + "\n")

        return "".join(stations)
