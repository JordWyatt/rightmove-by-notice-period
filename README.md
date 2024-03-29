# rightmove-by-notice-period

The lack of ability to filter by 'Date Available' on [RightMove](https://www.rightmove.co.uk/) encouraged me to hack this together.

It scrapes the result of a configured RightMove search, which can also take into account the date after you wish to move, and uploads the results to a worksheet on Google Sheets.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

To write to google sheets, you will need to configure access to the Sheets API for a service account, instructions to do so [can be found here](https://gspread.readthedocs.io/en/latest/oauth2.html#service-account).

To configure a search, create `configuration.ini` and edit as required:

```
[locations]
locationIdentifiers - Comma seperated RightMove location identifiers, you can grab this from your target search URL in a browser

[filters]
availableAfter - The date you want to filter properties by, only properties available on or after this date will be returned
availableAfterNWeeks - (OVERRIDES availableAfter) The number of weeks until you need to move, only properties available after this date will be returned
radius - Radius in miles
minPrice - Minimum Price
maxPrice - Maximum Price
minBedrooms - Minumum Beds
maxBedrooms - Maximum Beds
dontShow - Comma seperated string of property types to exclude, valid values: houseShare,retirement,student
furnishTypes - Comma seperated string of eligible furnishing types, valid values: furnished, unfurnished,partFurnished

[gspread]
serviceAccountConfigurationPath - Path to your Google API service account configuration
sheetName - Name of the sheet to write to

[mailer] (Optional, can be used to email results)
port - SMTP port
server - SMTP Server
login - SMTP User / Login
password - SMTP Password
sender - SMTP Sender
receiver - SMTP Receiver
```

for example:

```
[locations]
identifiers = REGION^93802,REGION^87521

[filters]
availableAfterNWeeks = 7
# availableAfter = 01/01/2023
radius=1
minPrice = 0
maxPrice = 1500
minBedrooms = 2
maxBedrooms = 3
dontShow=houseShare,retirement,student
furnishTypes=unfurnished,partFurnished

[gspread]
serviceAccountConfigurationPath=/Users/foobar/.config/gspread/service_account.json
sheetName=Rental Scraper

[mailer]
port=465
server=smtp.gmail.com
login=foobar@gmail.com
password=foobarssupersecretpassword
sender=sender@gmail.com
receiver=receiver@gmail.com
```

Once configured, the script can be executed periodically (using a CRON job for example).
