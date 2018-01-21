'''A client for Sbanken #openbanking. 

Import into your project and start doing banking from your
code. 

'''
import requests
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import logging
import configparser
logging.basicConfig(level=logging.DEBUG)

class SbankenError(Exception):
    pass

class SbankenAccount:
    'Objectify Sbanken account'
    # TODO: flesh out this and replace below


class SbankenClient:
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.customerId = config.get('secrets', 'customerId')
        # read all endpoints from config into a dict
        self.endpoints = { x:'{baseUrl}{endpoint}'.format(baseUrl=config.get('api', 'baseUrl'), endpoint=config.get('api', x)) for x in config.options('api')}
        logging.debug('endp: %r', self.endpoints)
        client_id = config.get('secrets', 'clientId')
        client_secret = config.get('secrets', 'password')
        auth = HTTPBasicAuth(client_id, client_secret)
        client = BackendApplicationClient(client_id=client_id)
        self.session = OAuth2Session(client=client)
        self.token = self.session.fetch_token(token_url=config.get('login', 'identityServer'), auth=auth)

    def __request(self, endpoint: str, method='GET', **kwargs):
        'internal method to run request through Oauth session, and return response body or raise error'
        r = self.session.request(url=self.endpoints.get(endpoint).format(**kwargs), method=method)
        if r.ok:  # got HTTP 200
            reply = r.json() 
            if not reply.get('isError'):
                # no api errors
                return reply
            # we have an error
            reply.remove('item')
            raise SbankenError(reply)
        else:
            raise SbankenError(r)

    @property
    def me(self) -> dict:
        'Return details about customer'
        return self.__request('customerDetails', customerId=self.customerId)

    def accounts(self):
        'Return a list of all accounts belonging to customer'
        return self.__request('accountList', customerId=self.customerId)

    def account(self, accountNumber: str) -> dict:
        'Return details from one account'
        return self.__request('accountDetails', customerId=self.customerId, accountNumber=accountNumber)

    def transactions(self, accountNumber: str) -> dict:
        'This operation returns the latest transactions of the given account within the time span set by the start and end date parameters.'
        # TODO add options index, length, startDate, endDate
        return self.__request('transactionList', customerId=self.customerId, accountNumber=accountNumber)

    def transfer(self, fromAccount: str, toAccount: str, amount: float, message: str) -> dict:
        '''Transfer money between your accounts, according to arguments
        
        The details of the transfer to be executed. The fields are as
        follows: 
        fromAccount: The account number of the account that the
        amount is to be transferred from, i.e. the debit account. This is a
        numerical string 11 characters long. The account number must be one
        of the accounts owned by the customer, or an account the customer has
        been granted access to. 
        toAccount: The account number of the account that the amount is to be
        transferred to, i.e. the credit account. This is a numerical string
        11 characters long. The account number must be one of the accounts
        owned by the customer, or an account the customer has been granted
        access to. 
        Amount: A decimal number representing the amount to be transferred.
        Must be equal to or greater than 1.00 and less than
        100000000000000000.00. Transfers with amounts in excess of the debit
        account availableamount will fail. Transfer currency is NOK. 
        Message: A description of the transfer. Must be between 1 and 30
        characters. The following characters are allowed:
        "1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZæÆøØåÅäÄëËïÏöÖüÜÿâÂêÊîÎôÔûÛãÃñÑõÕàÀèÈìÌòÒùÙáÁéÉíÍóÓýÝ,;.:!-/()?",
        and space. ''' 
        transferPayload = {
            'fromAccount': fromAccount,
            'toAccount': toAccount,
            'message':message,
            'amount':amount
        }
        r = self.session.post(self.endpoints.get('transferMethod').format(customerId=self.customerId),
                              json=transferPayload, # transfer as  JSON-Encoded POST/PATCH data
                              )
        if r.ok:
            return r.json() 
        else:
            raise SbankenError(r)

