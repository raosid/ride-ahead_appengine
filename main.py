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
        'scopes': "profile,history_lite",
    }
    url = generate_oauth_service().get_authorize_url(**params)
    return redirect(url)


@app.route('/redirect-uri', methods=['GET'])
def redirect_uri():
    # auth_code = request.args.get('code')
    # sesh['auth_code'] = auth_code
    # parameters = {
    #     'client_secret': 'sTe5UXYC1b5hC25CToNDzYkPOGljdl0RJoHrjrF8',
    #     'client_id': 'PQc6elZr9pVs1UcHizLEpIFtXcsrk6WN',
    #     'grant_type': 'authorization_code',
    #     'redirect_uri': 'https://rideahead-1152.appspot.com/redirect-uri',
    #     'code': auth_code
    # }
    # r = requests.post("https://login.uber.com/oauth/v2/token", params=parameters)
    # return r.json().get('access_token')

    params = {
        'client_id': "PQc6elZr9pVs1UcHizLEpIFtXcsrk6WN",
        'client_secret': "sTe5UXYC1b5hC25CToNDzYkPOGljdl0RJoHrjrF8",
        'redirect_uri': 'https://rideahead-1152.appspot.com/redirect-uri',
        'code': request.args.get('code'),
        'grant_type': 'authorization_code'
    }


    response = requests.post(
        'https://login.uber.com/oauth/token',
        data=params,
    )
    return response.json().get('access_token')





@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

app.secret_key = "sTe5UXYC1b5hC25CToNDzYkPOGljdl0RJoHrjrF8"
