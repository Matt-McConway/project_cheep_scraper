# Project Cheep - Scraper

Microservice created for [Project Cheep](https://github.com/json469/project_cheep) using data from [cheapies](https://www.cheapies.nz/).

Built with Python and run on Google's Cloud Platform, this service returns any coupons found for a given deal's node id.

It has since been expanded to store data in cloud firestore to reduce the number of times the function is called, as well as reduce the burden on the websites we are scraping.

## Usage
Make requests to the following endpoint: ```https://asia-northeast1-cheep-backend.cloudfunctions.net/get_coupon_code/?node_id=NODE_ID``` with a valid deal node id in the query string.

## Example requests/responses

Type | Example Query | Return Type | Example Response
---- | ------------- | ----------- | ----------------
Single | https://asia-northeast1-cheep-backend.cloudfunctions.net/get_coupon_code/?node_id=20931 | String | 'RRRFW72'
Multi | https://asia-northeast-cheep-backend.cloudfunctions.net/get_coupon_code/?node_id=20938 | Array | ["cs3019jfm", "NZAFFZERODEL"]
Invalid/None Found | https://asia-northeast-cheep-backend.cloudfunctions.net/get_coupon_code/?node_id=sfnjsnfsanfa | null | null


### Batch write function
In the case of the batch write function, you don't need to call it directly, as a cloud scheduler cron job makes it run every 30mins. To access this data, you just need to query our firestore db.


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
- Run ```gcloud functions deploy get_coupon_code --region=asia-northeast1 --runtime python37 --memory 128 --trigger-http```
- Or for rss pub/sub function: ```gcloud functions deploy get_cheapies_rss --region=asia-northeast1 --runtime python37 --memory 128 --trigger-topic cheapies-rss```
- Or for firestore coupon function: ```gcloud functions deploy get_coupon_codes_from_firestore --region=asia-northeast1 --runtime python37 --memory 128 --trigger-event providers/cloud.firestore/eventTypes/document.write --trigger-resource projects/cheep-backend/databases/\(default\)/documents/rss/cheapies```
- batch write function: ```gcloud functions deploy batch_write_deals_to_firestore --region=asia-northeast1 --runtime python37 --memory 128 --trigger-topic fetch-deals```

## Upcoming features
- [ ] Scraping comments (seperate function)
- [x] Store data on firebase - prevent repetitive scraping
- [ ] Testing
