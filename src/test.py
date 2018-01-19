
import requests
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

identityserver = "https://api.sbanken.no/identityserver/connect/token"

def o2(client_id, client_secret):
    auth = HTTPBasicAuth(client_id, client_secret)
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=identityserver, auth=auth)
    return token, oauth, client

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    import argparse

    parser = argparse.ArgumentParser(description="Grisebank")
    parser.add_argument('--clientId')
    parser.add_argument('--secret')
    parser.add_argument('--userId')

    args = parser.parse_args()

    o = o2(args.clientId, args.secret)
    print(o)