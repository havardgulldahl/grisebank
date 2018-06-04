'''A client for Sbanken #openbanking. 

Import into your project and start doing banking from your
code. 

'''
import jsonobject # pip install jsonobject
import requests   # pip install requests
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from urllib.parse import quote
import logging
import configparser
logging.basicConfig(level=logging.DEBUG)

class SbankenError(Exception):
    pass

class SbankenAccount(jsonobject.JsonObject):
    'Objectify Sbanken account'
    # properties defined in Sbanken json structs
    # {'accountNumber': '', # str
    # 'accountType': 'Standard account',
    # 'available': 0.01, # float
    # 'balance': 0.01, # float
    # 'creditLimit': 0.0,
    # 'customerId': '', # str, norwegian ssn
    # 'defaultAccount': False, # boolean
    # 'name': '', # str
    # 'ownerCustomerId': '' # str, norwegian ssn}
    accountNumber = jsonobject.StringProperty()
    accountType = jsonobject.StringProperty()
    available = jsonobject.FloatProperty()
    balance = jsonobject.FloatProperty()
    creditLimit = jsonobject.FloatProperty()
    customerId = jsonobject.StringProperty()
    defaultAccount = jsonobject.BooleanProperty()
    name = jsonobject.StringProperty()
    ownerCustomerId = jsonobject.StringProperty()

class Account:
    def __init__(self, client:'SbankenClient', accountData:dict):
        'Init the object with a SbankenClient object and a json dict '
        self.client = client
        self.details = SbankenAccount(accountData)

    def __str__(self) -> str:
        return '<Account: {}, account # {}>'.format(self.details.name, self.details.accountNumber)

    def update(self) -> None:
        'Get new details from server about balance etc'
        self.details  = self.client.accountDetails(self.details.accountNumber)

    def latest(self) -> list:
        'Return last transactions on the account'
        return self.client.transactions(self.details.accountNumber)

class SbankenPhoneNumber(jsonobject.JsonObject):
    'Sbanken Phone Number object'
    #                 {'countryCode': '', 'number': ''}], 
    countryCode = jsonobject.StringProperty()
    number = jsonobject.StringProperty()

class SbankenAddress(jsonobject.JsonObject):
    'Sbanken Address object'
    #{'addressLine1': '',
    #                 'addressLine2': '',
    #                 'addressLine3': '', 
    #                 'addressLine4': '', 
    #                 'city': None,
    #                 'country': '',
    #                 'zipCode': None},
    addressLine1 = jsonobject.StringProperty()
    addressLine2 = jsonobject.StringProperty()
    addressLine3 = jsonobject.StringProperty()
    addressLine4 = jsonobject.StringProperty()
    city = jsonobject.StringProperty()
    country = jsonobject.StringProperty()
    zipCode = jsonobject.StringProperty()

class SbankenUser(jsonobject.JsonObject):
    'Objectify Sbanken User'
    # properties defined in Sbanken json structs
    # {'customerId': '', # str, norwegian ssn
    # 'dateOfBirth': 'YYYY-MM-DDT00:00:00', # str, timestamp 
    # 'emailAddress': '', # str, email
    # 'firstName': '', # str
    # 'lastName': '', # str
    # 'phoneNumbers': [{'countryCode': '', 'number': ''},
    #                 {'countryCode': '', 'number': ''}],
    # 'postalAddress': {'addressLine1': '',
    #                 'addressLine2': '',
    #                 'addressLine3': '', 
    #                 'addressLine4': '', 
    #                 'city': None,
    #                 'country': '',
    #                 'zipCode': None},
    # 'streetAddress': {'addressLine1': '',
    #                 'addressLine2': '',
    #                 'addressLine3': None,
    #                 'addressLine4': None,
    #                 'city': '',
    #                 'country': None,
    #                 'zipCode': ''}
    customerId = jsonobject.StringProperty()
    dateOfBirth = jsonobject.DefaultProperty() # TODO: use DateTimeProperty()
    emailAddress = jsonobject.StringProperty()
    firstName = jsonobject.StringProperty()
    lastName = jsonobject.StringProperty()
    phoneNumbers = jsonobject.ListProperty(SbankenPhoneNumber)
    postalAddress = jsonobject.ObjectProperty(SbankenAddress)
    streetAddress = jsonobject.ObjectProperty(SbankenAddress)

class SbankenTransaction(jsonobject.JsonObject):
    'Objectify Sbanken Transaction'
    # properties defined in Sbanken json structs
    #  {'accountNumber': '', # str
    # 'accountingDate': '2018-01-22T00:00:00+01:00',
    # 'amount': 1.5, # float
    # 'customerId': '', # str, norwegian ssn
    # 'interestDate': '2018-01-21T00:00:00+01:00',
    # 'otherAccountNumber': None,
    # 'registrationDate': None,
    # 'text': '', # str
    # 'transactionId': '', # str
    # 'transactionType': 'RKI'} # one of RKI, 
    accountNumber = jsonobject.StringProperty()
    accountingDate = jsonobject.DefaultProperty() # TODO: use DateTimeProperty()
    amount = jsonobject.FloatProperty()
    customerId = jsonobject.StringProperty()
    interestDate = jsonobject.DefaultProperty() # TODO: use DateTimeProperty()
    otherAccountNumber = jsonobject.StringProperty()
    registrationDate = jsonobject.DefaultProperty() # TODO: use DateTimeProperty()
    text = jsonobject.StringProperty()
    transactionId = jsonobject.StringProperty()
    transactionType = jsonobject.StringProperty()

class SbankenClient:
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.customerId = config.get('secrets', 'customerId')
        # read all endpoints from config into a dict
        # TODO make this more readable
        self.endpoints = { x:'{baseUrl}{endpoint}'.format(baseUrl=config.get('api', 'baseUrl'), endpoint=config.get('api', x)) for x in config.options('api')}
        logging.debug('endp: %r', self.endpoints)
        # log in with oauth2 authentication
        client_id = quote(config.get('secrets', 'clientId'))
        client_secret = quote(config.get('secrets', 'password'))
        self.auth = HTTPBasicAuth(client_id, client_secret)
        client = BackendApplicationClient(client_id=client_id)
        self.session = OAuth2Session(client=client)
        self.fetch_token()

    def fetch_token(self):
        self.token = self.session.fetch_token(token_url=self.config.get('login', 'identityServer'), 
                                              auth=self.auth)

    def __request(self, endpoint: str, method='GET', customerId=None, **kwargs):
        'internal method to run request through Oauth session, and return response body or raise error'
        headers = {'User-Agent':'grisebank@lurtgjort.no'}
        if customerId is None:
            raise SbankenError('Need customerId for transaction')
        r = self.session.request(url=self.endpoints.get(endpoint).format(**kwargs), 
                                 method=method,
                                 headers={'customerId':customerId})

        #TODO: also add POST with json payload  --- see .transfer()
        if r.ok:  # got HTTP 200
            reply = r.json() 
            if not reply.get('isError'):
                # no api errors
                return reply
            # we have an error
            raise SbankenError(reply)
        else:
            raise SbankenError(r)

    @property
    def me(self) -> dict:
        'Return details about customer'
        r = self.__request('customerDetails', customerId=self.customerId)
        logging.debug('user:%r', r.get('item'))
        return SbankenUser(r.get('item'))

    def accounts(self) -> list:
        'Return a list of all accounts, as Account objects, belonging to customer'
        r = []
        for acct in self.__request('accountList', customerId=self.customerId).get('items'):
            r.append(Account(self, acct))
        return r

    def accountDetails(self, account: str) -> SbankenAccount:
        'Return details from one account'
        r = self.__request('accountDetails', customerId=self.customerId, accountNumber=account)
        return SbankenAccount(r.get('item'))

    def transactions(self, account: str) -> dict:
        'This operation returns the latest transactions of the given account within the time span set by the start and end date parameters.'
        # TODO add options index, length, startDate, endDate
        return [SbankenTransaction(t) for t in self.__request('transactionList', customerId=self.customerId, accountNumber=account).get('items')]

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
        if r.ok:  # got HTTP 200
            reply = r.json() 
            if not reply.get('isError'):
                # no api errors
                return reply
            # we have an error
            raise SbankenError(reply)
        else:
            raise SbankenError(r)

