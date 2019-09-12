# Project Cheep - Scraper

Microservice created for [Project Cheep](https://github.com/json469/project_cheep) using data from [cheapies](https://www.cheapies.nz/).

Built with Python and run on Google's Cloud Platform, this service returns any coupons found for a given deal's node id.

## Usage
Make requests to the following endpoint: ```https://us-central1-cheep-scraper.cloudfunctions.net/get_coupon_code/?node_id=NODE_ID``` with a valid deal node id in the query string.

## Example requests/responses

Type | Example Query | Return Type | Example Response
---- | ------------- | ----------- | ----------------
Single | https://us-central1-cheep-scraper.cloudfunctions.net/get_coupon_code/?node_id=20931 | String | 'RRRFW72'
Multi | https://us-central1-cheep-scraper.cloudfunctions.net/get_coupon_code/?node_id=20938 | Array | ["cs3019jfm", "NZAFFZERODEL"]
Invalid/None Found | https://us-central1-cheep-scraper.cloudfunctions.net/get_coupon_code/?node_id=sfnjsnfsanfa | null | null

## Development

### Dependencies
- Setup virtual environment: ```virtualenv env```
- Activate virtual environment: ```source env/bin/activate```
- Install dependencies: ```pip3 install -r requirements.txt```
- Add package: ```pip3 install package```
- Save packages: ```pip3 freeze > requirements.txt```

### Deployment
- Make sure you have the [gcloud sdk](https://cloud.google.com/sdk/) installed and in your PATH, and are logged in etc
- cd into the project directory
- Run ```gcloud functions deploy get_coupon_code --runtime python37 --trigger-http```

## Upcoming features
- Scraping comments (seperate function)
- Store data on firebase - prevent repetitive scraping
- Testing
