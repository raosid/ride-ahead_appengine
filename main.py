"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask
from flask import session as sesh
from flask import redirect
from flask import request, url_for
from flask import render_template
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from uber_rides.auth import AuthorizationCodeGrant
from rauth import OAuth2Service
import socket
import json
import requests
import httplib
import os
import urllib
import urllib2
from datetime import datetime
import parsedatetime as pdt
import time
app = Flask(__name__)
app.requests_session = requests.Session()
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


def generate_oauth_service():
    """Prepare the OAuth2Service that is used to make requests later."""
    return OAuth2Service(
        client_id="PQc6elZr9pVs1UcHizLEpIFtXcsrk6WN",
        client_secret="sTe5UXYC1b5hC25CToNDzYkPOGljdl0RJoHrjrF8",
        name='RideAhead',
        authorize_url="https://login.uber.com/oauth/authorize",
        access_token_url="https://login.uber.com/oauth/token",
        base_url="https://login.uber.com/"
    )


@app.route('/index')
def index():
    """Return a friendly HTTP greeting."""
    return render_template('index.html')

@app.route('/policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/authenticate')
def login():
    """
        Checks if the user is logged in or not. OAuth2.0
    """
    # auth_flow = {
    #     "response_type": 'code',
    #     "client_id": "PQc6elZr9pVs1UcHizLEpIFtXcsrk6WN",
    #     "redirect-uri": "https://rideahead-1152.appspot.com/redirect-uri"
    # }
    # auth_flow = json.dumps(auth_flow)
    # Working down here:
    # auth_flow = AuthorizationCodeGrant(
    #     "PQc6elZr9pVs1UcHizLEpIFtXcsrk6WN",
    #     {'profile', 'history'},
    #     "sTe5UXYC1b5hC25CToNDzYkPOGljdl0RJoHrjrF8",
    #     "https://rideahead-1152.appspot.com/redirect-uri"
    # )
    # auth_url = auth_flow.get_authorization_url()
    # return redirect(auth_url)
    params = {
        'response_type': 'code',
        'redirect_uri': 'https://rideahead-1152.appspot.com/redirect-uri',
        'scope': "profile",
    }
    url = generate_oauth_service().get_authorize_url(**params)
    return redirect(url)


@app.route('/redirect-uri', methods=['GET'])
def redirect_uri():
    parameters = {
        'redirect_uri': 'https://rideahead-1152.appspot.com/redirect-uri',
        'code': request.args.get('code'),
        'grant_type': 'authorization_code',
    }


    response = requests.post(
        'https://login.uber.com/oauth/token',
        auth=(
            'PQc6elZr9pVs1UcHizLEpIFtXcsrk6WN',
            'sTe5UXYC1b5hC25CToNDzYkPOGljdl0RJoHrjrF8'
        ),
        data=parameters
    )
    sesh['access_token'] = response.json().get('access_token')
    return redirect('/dashboard')



@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


#Helper methods
def get_latitude_and_longitude(event_location_natural):
    try:
        address_google = "https://maps.googleapis.com/maps/api/geocode/json?"
        params = {
            'address': event_location_natural,
            'key': "AIzaSyBtepcI0RCcD4urTJ8NGbcyC86GxTM_CTU"
        }
        url = address_google + urllib.urlencode(params)
        file_fetch = urllib2.urlopen(address_google + urllib.urlencode(params))
        return json.loads(file_fetch.read())
    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print "The server couldn't fulfill the request."
            print "Error code: ", e.code
        elif hasattr(e,'reason'):
            print "We failed to reach a server"
            print "Reason: ", e.reason
        return None

def fetch_latitude_and_logitude_from_dictionary(dictionary):
    try:
        lat =  dictionary["results"][0]["geometry"]["location"]["lat"]
        lng =  dictionary["results"][0]["geometry"]["location"]["lng"]
        return {'latitude': lat, 'longitude': lng}
    except:
        return {'message': 'Could not understand location'}


@app.route('/dashboard_webservice', methods=['POST'])
def dashboard_webservice():
    time_string = request.form['reminder_time']
    phone_number = request.form['phone_number']
    event_name = request.form['event_name']
    event_location_natural = request.form['event_location']

    #Getting the lat and long
    dictionary = get_latitude_and_longitude(event_location_natural)
    lat_and_long = fetch_latitude_and_logitude_from_dictionary(dictionary)
    if 'message' in lat_and_long:
        return json.dumps(lat_and_long)

    #Getting the time
    cal = pdt.Calendar()
    now = datetime.now()
    dt = cal.parseDT(time_string, now)[0]
    timestamp = dt.strftime("%s")

    parameters = {
      "reminder_time": timestamp,
      "phone_number": phone_number,
      "event": {
        "name": event_name,
        "location": event_location_natural,
        "latitude": lat_and_long['latitude'],
        "longitude": lat_and_long['longitude'],
        "time": timestamp
      }
    }

    url = "https://api.uber.com/v1/reminders?access_token=" + sesh['access_token']
    # params = {'access_token': sesh['access_token']}
    # final_url = url + urllib.urlencode(params)
    response = requests.post(
        url,
        headers={
            'content-type': 'application/json'
        },
        data=json.dumps(parameters)
    )

    return json.dumps(response.json())




@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

app.secret_key = os.urandom(24)
