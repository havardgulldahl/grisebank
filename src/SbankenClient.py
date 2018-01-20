
import requests
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import logging
logging.basicConfig(level=logging.DEBUG)

class SbankenError(Exception):
    pass

class SbankenClient:

    def __init__(self, config):
        self.config = config
        self.customerId = config.get('secrets', 'customerId')
        self.endpoints = { x:'{baseUrl}{endpoint}'.format(baseUrl=config.get('api', 'baseUrl'), endpoint=config.get('api', x)) for x in config.options('api')}
        logging.debug('endp: %r', self.endpoints)
        client_id = config.get('secrets', 'clientId')
        client_secret = config.get('secrets', 'password')
        auth = HTTPBasicAuth(client_id, client_secret)
        client = BackendApplicationClient(client_id=client_id)
        self.session = OAuth2Session(client=client)
        self.token = self.session.fetch_token(token_url=config.get('login', 'identityServer'), auth=auth)

    def __request(self, endpoint, method='GET', **kwargs):
        'internal method to run request through Oauth session, and return response body or raise error'
        r = self.session.request(url=self.endpoints.get(endpoint).format(**kwargs), method=method)
        if r.ok:
            return r.text 
        else:
            raise SbankenError(r)

    @property
    def me(self):
        'Return details about customer'
        return self.__request('customerDetails', customerId=self.customerId)

    def accounts(self):
        'Return a list of all accounts belonging to customer'
        return self.__request('accountList', customerId=self.customerId)

    def account(self, accountNumber):
        'Return details from one account'
        return self.__request('accountList', customerId=self.customerId, accountNumber=accountNumber)

    def transactions(self, accountNumber):
        'Return a list of last transactions from an account'
        return self.__request('transactionList', customerId=self.customerId, accountNumber=accountNumber)

    def transfer(self, transferPayload):
        '''Transfer money between your accounts, according to payload
        
        {
            "fromAccount": "string",
            "toAccount": "string",
            "message": "string",
            "amount": 0
        }
        '''
        r = self.session.post(self.endpoints.get('transferMethod').format(customerId=self.customerId),
                              data=transferPayload)
        if r.ok:
            return r.text 
        else:
            raise SbankenError(r)

