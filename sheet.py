import gspread

headers = ["Date Scraped", "URL", "Description", "Price", "Location",
           "Nearest Station(s)", "Date Available", "Furnished", "Deposit"]

propertyMappings = {
    "Date Scraped": "date_scraped",
    "URL": "url",
    "Description": "description",
    "Price": "price",
    "Location": "location",
    "Nearest Station(s)": "nearest_stations",
    "Date Available": "date_available",
    "Furnished": "furnished",
    "Deposit": "deposit",
}


class Sheet:
    def __init__(self, service_account_configuration_path, sheet_name):
        gc = gspread.service_account(service_account_configuration_path)
        self.worksheet = gc.open(sheet_name).sheet1

        if(self.worksheet.acell("A1").value != headers[0]):
            self.write_headers()

    def write_headers(self):
        self.worksheet.format(
            "A1:I1", {'textFormat': {"bold": True, "italic": True}})
        self.worksheet.update('A1:I1', [headers])

    def does_cell_exist_with_value(self, value):
        try:
            self.worksheet.find(value)
            return True
        except gspread.exceptions.CellNotFound:
            return False

    def add_listings(self, listings):
        print("Writing listings to sheet...")
        duplicates = 0
        written = 0
        for listing in listings:
            is_existing_listing = self.does_cell_exist_with_value(listing.url)
            if(not is_existing_listing):
                row = self.build_row(listing)
                self.worksheet.insert_row(row, 2)
                written += 1
            else:
                duplicates += 1

        return (written, duplicates)

    def build_row(self, listing):
        row = []
        listing_details = vars(listing)
        for _, attribute in propertyMappings.items():
            row.append(listing_details[attribute])

        return row
