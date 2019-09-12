import sys
import json

from flask import escape
from flask import abort
import requests
from lxml import html

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
        coupon = tree.xpath('//div[@title="Coupon code"]/strong/text()') # Xpath search for single coupon 
        coupons = tree.xpath('//div[@title="Coupon codes"]/strong/text()') # Multiple coupons have a slightly different title property
        
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


   