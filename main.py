import sys
import json

from flask import escape
from flask import abort
import requests
from lxml import html
from google.cloud import firestore

def get_coupon_code(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The incoming request as a flask Request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    Usage:
        Basically your request should contain a cheapies node id that you wish to scrape
        for the coupon code. If it finds any codes embeded in the page, it will return them in JSON format.
    """

    BASE_URL = "https://www.cheapies.nz/node/"

    if request.method == 'OPTIONS':
        # Handle CORS - not entirely sure I have this correct, but no longer getting the issue
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': 3600
        }
        response = ''
        return (response, 204, headers)
    elif request.method == 'GET':
        query_string = request.args
        if query_string and 'node_id' in query_string:
            node_id = query_string['node_id']
            print('get_coupon_code - Querying node_id - %s' % node_id)
        else:
            print('get_coupon_code - Bad Request - Missing node_id in query string')
            return abort(400)
        
        # From here, method is confirmed to be GET, with query string that contains a node_id
        page = requests.get("%s%s" %(BASE_URL, node_id)) # Make the call to get page data for that node's page
        try:
            page.raise_for_status()
        except Exception as exc:
            print('get_coupon_code - Issue when querying node_id (%s) There was a problem: %s' % (node_id, exc))
        
        # Parse page content into a tree for scraping
        tree = html.fromstring(page.content)
        coupon = tree.xpath('//div[contains(@title,"Coupon code")]/strong/text()') # Xpath search for single coupon 
        coupons = tree.xpath('//div[contains(@title,"Coupon codes")]/strong/text()') # Nodes with multiple coupons have a slightly different title
        
        # CORS header - again, not sure if I have this right
        headers = {
            'Access-Control-Allow-Origin': '*'
        }

        if len(coupon) == 1:
            print('get_coupon_code - return 200 - Found 1 coupon - %s' % coupon)
            return (coupon[0], 200, headers)
        elif len(coupons) >= 1:
            print('get_coupon_code - return 200 - Found 1 or more coupons - %s' % coupons)
            return (json.dumps(coupons), 200, headers)
        else:
            print('get_coupon_code - return 204 - No coupons found')
            return ('', 204, headers)
    elif request.method == 'PUT':
        print('get_coupon_code - return 405 - Request Method Error - Expected GET, got PUT')
        return abort(405)
    elif request.method == 'POST':
        print('get_coupon_code - return 405 - Request Method Error - Expected GET, got POST')
        return abort(405)
    elif request.method == 'DELETE':
        print('get_coupon_code - return 405 - Request Method Error - Expected GET, got DELETE')
        return abort(405)
    else:
        print('get_coupon_code - return 500 - General Error - :(')
        return abort(500)

def batch_write_deals_to_firestore(event, context):
    """Background Cloud Function, triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    Incoming Payload:
        {
            "Websites": [
                {
                "Name": "cheapies",
                "URL": "https://www.cheapies.nz/deals/feed"
                }
            ]
        }
    
    TODO: Few more tweaks to make it easier to maintain when adding new websites to scrape
    """
    import base64
    import json

    # Helper functions start
    def get_cheapies_nodes_from_xml(xml):
        tree = html.fromstring(xml)
        nodeLinks = tree.xpath('//link[not(contains(text(),"deal"))]')
        nodeLinks = nodeLinks[2:]
        nodes = []
        for link in nodeLinks:
            nodes.append(str(html.tostring(link))[37:][:-4])
        # Helper function that scrapes gets nodes from cheapies xml
        return nodes
    
    def get_cheapies_codes_from_node(nodeID, BASE_URL):
        if BASE_URL.__contains__('cheapies'):
            page = requests.get('https://www.cheapies.nz/node/%s' % nodeID)
            try:
                page.raise_for_status()
            except Exception as exc:
                print('get_cheapies_rss - Issue when querying node %s. There was a problem: %s' % (nodeID, exc))
            tree = html.fromstring(page.content)
            coupons = tree.xpath('//div[contains(@title,"Coupon code")]/strong/text()')  

            return coupons
        else:
            return []

    # Helper functions end
    print("""This Function was triggered by messageId {} published at {}
    """.format(context.event_id, context.timestamp))

    DATA_TO_WRITE = []

    if 'data' in event:
        payload = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    
        for site in payload['Websites']:
            SITE_NAME = site['Name']
            BASE_URL = site['URL']

            page = requests.get(BASE_URL)
            try:
                page.raise_for_status()
            except Exception as exc:
                print('get_cheapies_rss - Issue when querying RSS Feed. There was a problem: %s' % (exc))
            
            nodes = get_cheapies_nodes_from_xml(page.content)

            codes = [{"Node": i, "Codes": get_cheapies_codes_from_node(i, BASE_URL)} for i in nodes]
            DATA_TO_WRITE.append({
                "Name": SITE_NAME,
                "RSS": page.text,
                "Codes": codes
            })
    db = firestore.Client()
    batch = db.batch()
    print('Batch starting')
    for payload in DATA_TO_WRITE:
        rss_ref = db.collection(payload["Name"]).document('RSS')
        batch.set(rss_ref, {'Content': payload["RSS"]})

        codes_ref = db.collection(payload["Name"]).document('Codes')
        batch.set(codes_ref, {'Content': payload["Codes"]})

    batch.commit()
    print('Batch committed')
