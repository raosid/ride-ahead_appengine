"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask
from flask import session as sesh
from flask import redirect
from flask import request, url_for
from flask import render_template
app = Flask(__name__)
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from uber_rides.auth import AuthorizationCodeGrant
import socket
import json
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


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
    auth_flow = AuthorizationCodeGrant(
        "PQc6elZr9pVs1UcHizLEpIFtXcsrk6WN",
        {'profile', 'history'},
        "sTe5UXYC1b5hC25CToNDzYkPOGljdl0RJoHrjrF8",
        "https://rideahead-1152.appspot.com/redirect-uri"
    )
    auth_url = auth_flow.get_authorization_url()
    session = auth_flow.get_session(auth_url)

    # sesh['redirect_url'] = auth_url
    # return redirect(auth_url)


@app.route('/redirect-uri', methods=['GET'])
def redirect_uri():
    access_token = request.args.get('code', '')
    sesh['access_token'] = access_token
    if len(access_token) > 0: # a valid access token

        return credentials
    else:
        return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

app.secret_key = "sTe5UXYC1b5hC25CToNDzYkPOGljdl0RJoHrjrF8"
